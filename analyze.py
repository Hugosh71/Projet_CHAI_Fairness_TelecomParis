import argparse


def main():
    parser = argparse.ArgumentParser(description="CHAI Fairness Project Analysis Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # summary command
    parser_summary = subparsers.add_parser(
        "summary", help="Summarize fairness AMR file"
    )
    parser_summary.add_argument(
        "input_file", type=str, help="Input AMR file for summary analysis"
    )

    # centrality_score command
    parser_centrality = subparsers.add_parser(
        "centrality_score", help="Top K fairness centrality score"
    )
    parser_centrality.add_argument(
        "input_file", type=str, help="Input AMR file for centrality analysis"
    )
    parser_centrality.add_argument(
        "--k", type=int, default=10, help="Number of top results to show (default: 10)"
    )

    args = parser.parse_args()

    if args.command == "summary":
        from analysis import analyze_fairness_amr

        analyze_fairness_amr(args.input_file)
    elif args.command == "centrality_score":
        from analysis import top_k_fairness_graphs

        print(top_k_fairness_graphs(args.input_file, args.k))
    else:
        parser.print_help()
        exit(1)


if __name__ == "__main__":
    main()
