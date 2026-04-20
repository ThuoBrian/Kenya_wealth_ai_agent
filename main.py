#!/usr/bin/env python3
"""
Kenya Wealth & Finance Agent - CLI Entry Point

Run this file to start the interactive financial advisor.
"""

from datetime import datetime

from agent import KenyaWealthAgent
from config import get_config, list_available_models
from templates.html import save_html_report
from utils.display import (
    print_header,
    print_section_header,
    print_menu_item,
    print_success,
    print_error,
    print_info,
    print_divider,
)
from utils.display import Fore, Style


def main() -> None:
    """Main function to run the Kenya Wealth Agent."""
    # Load configuration
    config = get_config()

    print_header()

    # Check Ollama connection using config
    model = config.model
    base_url = config.base_url

    try:
        agent = KenyaWealthAgent(model=model, base_url=base_url)
        # Test connection by listing models
        agent.client.list()
    except Exception as e:
        print_error("Could not connect to Ollama. Please ensure Ollama is running:")
        print(f"\n   {Fore.WHITE}1.{Style.RESET_ALL} Install Ollama from {Fore.CYAN}https://ollama.ai{Style.RESET_ALL}")
        print(f"   {Fore.WHITE}2.{Style.RESET_ALL} Run: {Fore.YELLOW}ollama pull {model}{Style.RESET_ALL}")
        print(f"   {Fore.WHITE}3.{Style.RESET_ALL} Ollama should be running at {Fore.CYAN}{base_url}{Style.RESET_ALL}")
        print(f"\n   {Fore.RED}Error:{Style.RESET_ALL} {e}")
        print(f"\n   {Fore.YELLOW}Tip:{Style.RESET_ALL} Change model in {Fore.CYAN}config.ini{Style.RESET_ALL} file")
        return

    print_success(f"Connected to Ollama model: {Fore.YELLOW}{model}{Style.RESET_ALL}")

    print_section_header("I Can Help You With", "🎯")
    print_menu_item("budget", "Analyze your budget and spending")
    print_menu_item("invest", "Get investment recommendations")
    print_menu_item("emergency", "Calculate emergency fund target")
    print_menu_item("tax", "Calculate your taxes (PAYE)")
    print_menu_item("retirement", "Plan for retirement")
    print_menu_item("savings", "Savings strategies")

    print()
    print_divider("─")
    print_info("Type 'quit' to exit and generate report, 'help' for commands")
    print_divider("─")

    # Track session start time
    session_start = datetime.now()

    while True:
        try:
            print()
            user_input = input(f"{Fore.CYAN}┌─{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT} You{Style.RESET_ALL}\n{Fore.CYAN}└─{Style.RESET_ALL} ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "bye"):
                print()
                print(f"{Fore.GREEN}{'─' * 60}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}🇰🇪 {Fore.WHITE}Thank you for using Kenya Wealth Agent!{Style.RESET_ALL}")
                print(f"{Fore.GREEN}   Best of luck with your financial journey!{Style.RESET_ALL}")
                print(f"{Fore.GREEN}{'─' * 60}{Style.RESET_ALL}")

                # Generate final report on exit
                if agent.get_conversation_history():
                    summary = agent.summarize_conversation()
                    report_path = save_html_report(
                        agent.get_conversation_history(),
                        session_start,
                        summary=summary,
                    )
                    print()
                    print(f"{Fore.CYAN}📄 Session report saved to: {Fore.WHITE}{report_path}{Style.RESET_ALL}")
                else:
                    print()
                    print(f"{Fore.YELLOW}ℹ No conversation to save.{Style.RESET_ALL}")
                break

            if user_input.lower() == "help":
                print()
                print_section_header("Available Commands", "📋")
                print_menu_item("budget", "Analyze your budget", Fore.GREEN)
                print_menu_item("invest", "Get investment recommendations", Fore.GREEN)
                print_menu_item("emergency", "Calculate emergency fund target", Fore.GREEN)
                print_menu_item("tax", "Calculate your taxes", Fore.GREEN)
                print_menu_item("reset", "Start a new conversation", Fore.YELLOW)
                print_menu_item("models", "Show available models", Fore.CYAN)
                print_menu_item("config", "Show current configuration", Fore.CYAN)
                print_menu_item("quit", "Exit and generate report", Fore.RED)
                continue

            if user_input.lower() == "models":
                print()
                print_section_header("Available Models", "🤖")
                print(f"  {'Alias':<15} {'Model Name':<30}")
                print(f"  {'─' * 45}")
                from config import AVAILABLE_MODELS
                for alias, model_name in AVAILABLE_MODELS.items():
                    current = " (current)" if model_name == config.model else ""
                    print(f"  {Fore.CYAN}{alias:<15}{Style.RESET_ALL} {model_name}{current}")
                print()
                print_info(f"Change model in {Fore.CYAN}config.ini{Style.RESET_ALL} file")
                continue

            if user_input.lower() == "config":
                print()
                print_section_header("Current Configuration", "⚙️")
                print(f"  {'Setting':<20} {'Value':<40}")
                print(f"  {'─' * 60}")
                print(f"  {Fore.CYAN}{'Model':<20}{Style.RESET_ALL} {config.model}")
                print(f"  {Fore.CYAN}{'Base URL':<20}{Style.RESET_ALL} {config.base_url}")
                print(f"  {Fore.CYAN}{'Developer':<20}{Style.RESET_ALL} {config.developer_name}")
                print(f"  {Fore.CYAN}{'Version':<20}{Style.RESET_ALL} {config.version}")
                print(f"  {Fore.CYAN}{'Output Dir':<20}{Style.RESET_ALL} {config.output_dir}")
                print()
                print_info(f"Edit {Fore.CYAN}config.ini{Style.RESET_ALL} to change settings")
                continue

            if user_input.lower() == "reset":
                agent.reset_conversation()
                session_start = datetime.now()  # Reset session start time
                print()
                print_success("Conversation reset. Starting fresh!")
                continue

            # Get response from agent
            response = agent.chat(user_input)
            print()
            print(f"{Fore.MAGENTA}┌─{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT} 💡 Advisor{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}│{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}└─{Style.RESET_ALL} {response}")
            print_divider("─")

        except KeyboardInterrupt:
            print(f"\n\n{Fore.GREEN}👋 Thank you for using Kenya Wealth Agent!{Style.RESET_ALL}")

            # Generate final report on Ctrl+C exit too
            if agent.get_conversation_history():
                summary = agent.summarize_conversation()
                report_path = save_html_report(
                    agent.get_conversation_history(),
                    session_start,
                    summary=summary,
                )
                print(f"{Fore.CYAN}📄 Session report saved to: {Fore.WHITE}{report_path}{Style.RESET_ALL}")
            break
        except Exception as e:
            print()
            print_error(f"Error: {e}")
            print_info("Please try again or type 'quit' to exit.")


if __name__ == "__main__":
    main()