from .config import get_config, startup_wizard
from .logging import start_logger
from .utils import *
from .indexing import Indexer
from .rag import OBRAG

from typing import List, Any
from logging import Logger

def interaction_loop(pipeline: OBRAG, logger: Logger) -> None:
    """Main interaction loop for the OBRAG CLI."""
    message_history : List[Any] = [SYSTEM_MESSAGE]
    while True:
        try:
            question = input("\nyou (type 'exit' to quit): ").strip()
            if question.lower() == "exit":
                print("closing OBRAG...")
                logger.info("User exited the OBRAG CLI.")
                break
            
            logger.info(f"Received question: {question}")
            response, message_history, tools_called = pipeline.generate(question, message_history)
            
            
            print("\nOBRAG:")
            print(response)

            print("\nTools called:")
            print(", ".join(tools_called))
        except Exception as e:
            logger.error(f"Error during interaction: {e}")
            print(f"An error occurred: {e}. Please try again.")


def main():
    print_banner()
    args = get_args()
    cfg = get_config()
    logger = start_logger()
    logger.info("OBRAG CLI started.")

    logger.info(f"Verifying configuration...")

    if cfg.first_run:
        logger.info("First run detected. Starting configuration wizard...")
        startup_wizard(cfg, logger)
        logger.info("Configuration wizard completed.")
        print_banner()
    
    if args.reconfigure:
        logger.info("Reconfiguring OBRAG settings...")
        print("Reconfigure flag passed...")
        startup_wizard(cfg, logger)
        logger.info("Reconfiguration completed.")
        print_banner()
    
    # set api key at runtime
    os.environ["OPENAI_API_KEY"] = cfg.openai_api_key

    # move on to loading vstore, building if necessary
    print(f"\nUpdating and loading vector store from [{cfg.persist_dir}]...")
    indexer = Indexer(cfg, logger)
    result, vstore = indexer.get_vstore(force_refresh=args.rebuild) # Load or build the vector store
    print("Vector store loaded successfully.")
    print(f"Indexing Results: {result}")

    # compile the RAG pipeline and start the CLI
    rag = OBRAG(vstore, cfg, logger)
    print("RAG pipeline compiled successfully.")
    logger.info("OBRAG CLI is ready to answer questions.")

    clear_console()
    print_banner()

    if not args.ask:
        interaction_loop(rag, logger)
    
    else:
        question = args.ask.strip()
        logger.info(f"Direct question asked: {question}")
        answer, _, tools_called = rag.generate(question, [SYSTEM_MESSAGE])

        print("\nOBRAG:")
        print(answer)
        logger.info(f"Answer generated: {answer}")

        print("\nTools Called:")
        print(", ".join(tools_called))
        
        logger.info("exiting after direct question response.")


if __name__ == "__main__":
    main()