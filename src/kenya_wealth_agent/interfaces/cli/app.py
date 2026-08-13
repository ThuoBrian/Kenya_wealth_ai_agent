"""Command-line entry point for Kenya Wealth Agent."""

import argparse
import sys

from kenya_wealth_agent.domain import FinancialGoal
from kenya_wealth_agent.interfaces.cli import commands


def _build_parser() -> argparse.ArgumentParser:
    """Build the argparse CLI."""
    parser = argparse.ArgumentParser(
        prog="kenya-wealth-agent",
        description="Kenya Wealth Agent — AI financial advisor for the Kenyan market",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # web
    web_parser = subparsers.add_parser("web", help="Start the FastAPI web server")
    web_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the web server (default: 127.0.0.1)",
    )
    web_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the web server (default: 8000)",
    )
    web_parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable uvicorn auto-reload for development",
    )

    # chat
    subparsers.add_parser("chat", help="Run an interactive CLI chat session")

    # tax
    tax_parser = subparsers.add_parser("tax", help="Calculate PAYE and deductions")
    tax_parser.add_argument(
        "--gross-salary",
        type=float,
        required=True,
        help="Gross monthly salary in KES",
    )

    # budget
    budget_parser = subparsers.add_parser("budget", help="Analyze a budget")
    budget_parser.add_argument(
        "--income",
        type=float,
        required=True,
        help="Total monthly income in KES",
    )
    budget_parser.add_argument(
        "--expenses",
        type=str,
        required=True,
        help='JSON object of expenses, e.g. \'{"rent": 50000, "food": 20000}\'',
    )

    # invest
    invest_parser = subparsers.add_parser("invest", help="Get investment recommendations")
    invest_parser.add_argument(
        "--amount",
        type=float,
        required=True,
        help="Amount to invest in KES",
    )
    invest_parser.add_argument(
        "--risk",
        type=str,
        required=True,
        choices=["conservative", "moderate", "aggressive"],
        help="Risk tolerance",
    )
    invest_parser.add_argument(
        "--timeline",
        type=str,
        required=True,
        help="Investment timeline, e.g. 'short term' or '10+ years'",
    )

    # emergency
    emergency_parser = subparsers.add_parser("emergency", help="Calculate an emergency fund target")
    emergency_parser.add_argument(
        "--monthly-expenses",
        type=float,
        required=True,
        help="Monthly expenses in KES",
    )
    emergency_parser.add_argument(
        "--months",
        type=int,
        default=6,
        help="Months of expenses to cover (default: 6)",
    )

    # retirement
    retirement_parser = subparsers.add_parser("retirement", help="Project retirement savings")
    retirement_parser.add_argument(
        "--current-age",
        type=int,
        required=True,
        help="Current age",
    )
    retirement_parser.add_argument(
        "--retirement-age",
        type=int,
        required=True,
        help="Target retirement age",
    )
    retirement_parser.add_argument(
        "--monthly-contribution",
        type=float,
        required=True,
        help="Monthly contribution in KES",
    )
    retirement_parser.add_argument(
        "--rate",
        type=float,
        default=0.09,
        help="Annual return rate (default: 0.09)",
    )

    # savings
    savings_parser = subparsers.add_parser("savings", help="Recommend a savings strategy")
    savings_parser.add_argument(
        "--goal",
        type=str,
        required=True,
        choices=[g.value for g in FinancialGoal],
        help="Financial goal",
    )
    savings_parser.add_argument(
        "--target-amount",
        type=float,
        required=True,
        help="Target amount in KES",
    )
    savings_parser.add_argument(
        "--timeline-months",
        type=int,
        required=True,
        help="Timeline in months",
    )

    # export
    export_parser = subparsers.add_parser("export", help="Export the chat session to HTML")
    export_parser.add_argument(
        "--session-id",
        type=str,
        default="cli-session",
        help="Session id to export (default: cli-session)",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the appropriate command."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "web":
            commands.run_web(host=args.host, port=args.port, reload=args.reload)
        elif args.command == "chat":
            commands.run_chat()
        elif args.command == "tax":
            commands.run_tax(gross_salary=args.gross_salary)
        elif args.command == "budget":
            commands.run_budget(income=args.income, expenses=args.expenses)
        elif args.command == "invest":
            commands.run_invest(
                amount=args.amount,
                risk_tolerance=args.risk,
                timeline=args.timeline,
            )
        elif args.command == "emergency":
            commands.run_emergency(
                monthly_expenses=args.monthly_expenses,
                months=args.months,
            )
        elif args.command == "retirement":
            commands.run_retirement(
                current_age=args.current_age,
                retirement_age=args.retirement_age,
                monthly_contribution=args.monthly_contribution,
                annual_return_rate=args.rate,
            )
        elif args.command == "savings":
            commands.run_savings(
                goal=args.goal,
                target_amount=args.target_amount,
                timeline_months=args.timeline_months,
            )
        elif args.command == "export":
            commands.run_export(session_id=args.session_id)
        else:
            parser.print_help()
            return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
