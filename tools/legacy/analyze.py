import argparse

from src.analyzer import StockAnalyzer
from src.config_loader import ConfigLoader
from src.logger import setup_logger


def main():
    # 引数解析
    parser = argparse.ArgumentParser(description="Stock Analyzer Auto-Runner")
    parser.add_argument(
        "--debug", action="store_true", help="Run in debug mode (Mock AI)"
    )
    parser.add_argument(
        "--top", type=int, help="Analyze only top N stocks (e.g. --top 5)"
    )  # [追加]
    args = parser.parse_args()

    # ロガー設定 (画面とファイルに出力)
    logger = setup_logger()
    logger.info(f"🚀 Starting Analysis... (Debug: {args.debug}, Top: {args.top})")

    try:
        # 設定読み込み
        config_loader = ConfigLoader("config.yaml")
        config = config_loader.config

        if not config:
            logger.error("❌ Failed to load config.yaml")
            return

        # 分析実行
        analyzer = StockAnalyzer(config, debug_mode=args.debug)
        # [修正] limit引数を渡す
        analyzer.run_analysis(limit=args.top)

    except Exception as e:
        logger.error(f"❌ Critical Error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
