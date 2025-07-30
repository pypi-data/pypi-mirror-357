from sfn_blueprint.utils.llm_handler.llm_clients import *
from sfn_blueprint.utils.logging import setup_logger
from sfn_blueprint.config.model_config import MODEL_CONFIG, SUPPORT_MESSAGE
from sfn_blueprint.utils.llm_response_formatter import llm_response_formatter
class SFNAIHandler:
    def __init__(self, logger_name="SFNAIHandler"):
        self.logger, _ = setup_logger(logger_name)
        self.client_map = {
            'openai': sfn_openai_client,
            'anthropic': sfn_anthropic_client,
            'cortex': sfn_cortex_client
        }

    def route_to(self, llm_provider, configuration, model,db_url=None):
        """Routes requests to the appropriate LLM provider and send chat completion requests to LLM.
            :param configuration : dict
                A dictionary containing the following keys:
                - messages (mandatory): A list of dictionaries where each dictionary represents a message. 
                    Each message must contain a "role" (e.g., "system" or "user") and "content" (the message text).
                - temperature (optional): Controls the creativity of the responses. If not provided, 
                    the default value is 0.7.
                - max_tokens (optional): The maximum number of tokens to generate in the response. 
                    If not provided, the default value is 1000.

            :param model : str
                The Anthropic model to be used for generating the chat completion. This is a mandatory parameter.

            :return : 
                response : dict containing the generated text and other metadata.
                token_cost_summary : dict contains api cost
        """

        self.logger.info(f"Routing request to {llm_provider} using model {model}")
        
        if llm_provider not in self.client_map and llm_provider != 'cortex':
            self.logger.error(f"Unsupported LLM provider: {llm_provider} - {SUPPORT_MESSAGE}")
            return

        model_config = MODEL_CONFIG['suggestions_generator'][llm_provider]
        session = None
        if llm_provider == 'cortex':
            session = get_snowflake_session(db_url)

        try:
            llm_client = self.client_map[llm_provider](model)
            response, token_cost_summary = llm_client.chat_completion(
                messages=configuration["messages"],
                temperature=configuration.get("temperature", model_config['temperature']),
                max_tokens=configuration.get("max_tokens", model_config['max_tokens']),
                model=model,
                retries=model_config['max_attempt'],
                retry_delay=model_config['retry_delay'],
                session=session
            )

            self.logger.info(f"Received response from {llm_provider}: {response}")
            response = llm_response_formatter(response, llm_provider, self.logger)         
            return response, token_cost_summary
        except Exception as e:
            self.logger.error(f"Error while executing API call to {llm_provider}: {e}")
            raise

