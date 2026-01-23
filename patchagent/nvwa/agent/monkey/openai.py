import random
import os

from langchain_core.agents import AgentAction, AgentFinish
from langchain_classic.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_classic.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_classic.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages

from nvwa.logger import log
from nvwa.agent.base import BaseAgent
from nvwa.context import Context, ContextManager
from nvwa.proxy.default import create_locate_tool, create_validate_tool, create_viewcode_tool
from nvwa.agent.monkey.prompt import (
    MONKEY_SYSTEM_PROMPT_TEMPLATE,
    MONKEY_USER_PROMPT_TEMPLATE,
)


class MonkeyOpenAIAgent(BaseAgent):
    def __init__(
        self,
        context_manager: ContextManager,
        model: str = "qwen-turbo",
        temperature: float = 1,
        auto_hint: bool = False,
        counterexample_num: int = 3,
        locate_tool: bool = True,
        max_iterations: int = 30,
    ):
        super().__init__(context_manager)

        self.model = model
        self.temperature = temperature
        self.auto_hint = auto_hint
        self.counterexample_num = counterexample_num
        self.locate_tool = locate_tool
        self.max_iterations = max_iterations
        self.error_cases = self.get_previous_error_cases()
        
        # 加载Qwen API配置
        self.qwen_api_key = os.getenv("QWEN_API_KEY")
        self.qwen_api_base = os.getenv("QWEN_API_BASE")
        
        # 根据配置初始化LLM
        if self.qwen_api_key and self.qwen_api_base:
            # 使用Qwen API
            self.llm = ChatOpenAI(
                temperature=self.temperature,
                model=self.model,
                api_key=self.qwen_api_key,
                base_url=self.qwen_api_base
            )
        else:
            # 使用默认OpenAI配置
            self.llm = ChatOpenAI(temperature=self.temperature, model=self.model)

    def setup(self, context: Context):
        lc_tools = [
            create_viewcode_tool(context, auto_hint=self.auto_hint),
            create_validate_tool(context, auto_hint=self.auto_hint),
        ]
        if self.locate_tool:
            lc_tools.append(create_locate_tool(context, auto_hint=self.auto_hint))
        oai_tools = [convert_to_openai_tool(tool) for tool in lc_tools]

        if self.locate_tool:
            self.prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", MONKEY_SYSTEM_PROMPT_TEMPLATE),
                    ("user", MONKEY_USER_PROMPT_TEMPLATE),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )
            context.add_system_message(MONKEY_SYSTEM_PROMPT_TEMPLATE.format())
        else:
            self.prompt = ChatPromptTemplate.from_messages(
                [
                    ("user", MONKEY_USER_PROMPT_TEMPLATE),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )

        context.add_user_message(
            MONKEY_USER_PROMPT_TEMPLATE.format(
                project=context.task.project,
                tag=context.task.tag,
                report=context.task.sanitizer_report.summary,  # type: ignore
                error_cases=self.error_cases,
            )
        )

        self.llm_with_tool = self.llm.bind_tools(tools=oai_tools)
        
        def save_agent_output(output):
            if isinstance(output, AgentFinish):
                context.add_llm_response(output.log)
            else:
                if not isinstance(output, list):
                    log.error(f"Invalid output: {output}")
                else:
                    for action in output:
                        if isinstance(action, AgentAction):
                            context.add_llm_response(action.log)
                        else:
                            log.error(f"Invalid action: {action}")

            return output

        self.agent = (
            {
                "project": lambda input: context.task.project,
                "tag": lambda input: context.task.tag,
                "report": lambda input: context.task.sanitizer_report.summary,  # type: ignore
                "error_cases": lambda input: self.error_cases,
                "agent_scratchpad": lambda input: format_to_openai_tool_messages(input["intermediate_steps"]),
            }
            | self.prompt
            | self.llm_with_tool
            | OpenAIToolsAgentOutputParser()
            | save_agent_output
        )

        self.agent_executor = AgentExecutor(agent=self.agent, tools=lc_tools, verbose=True, max_iterations=self.max_iterations)  # type: ignore

    def get_previous_error_cases(self):
        error_cases = []
        for context in self.context_manager.contexts:
            for tool_call in context.tool_calls:
                if tool_call["name"] == "validate":
                    error_cases.append(f"Error case: \n{tool_call['args']['patch']}")

        error_cases = random.sample(error_cases, min(self.counterexample_num, len(error_cases)))
        if len(error_cases) == 0:
            return ""

        hint = "Here are some wrong patches you generated previously, you CAN NOT use them again:\n"
        error_message = hint + "\n".join(error_cases)
        log.purple(f"[{self.__class__.__name__}] Error cases: \n" + error_message)
        return error_message

    def _apply(self):
        log.info(
            f"Applying {self.__class__.__name__} (model: {self.model}, temperature: {self.temperature}, auto_hint: {self.auto_hint}, counterexample_num: {self.counterexample_num}, locate_tool: {self.locate_tool})"
        )

        with self.context_manager.new_context() as context:
            self.setup(context)
            _ = self.agent_executor.invoke({})


