import ccxt

from trading.exchanges.exchange_manager import ExchangeManager
from evaluator.symbol_evaluator import SymbolEvaluator
from trading.trader.trader_simulator import TraderSimulator
from evaluator.cryptocurrency_evaluator import CryptocurrencyEvaluator
from evaluator.evaluator_creator import EvaluatorCreator
from tests.test_utils.config import load_test_config
from evaluator.Util.advanced_manager import AdvancedManager
from trading.trader.portfolio import Portfolio
from evaluator.Updaters.symbol_time_frames_updater import SymbolTimeFramesDataUpdaterThread
from evaluator.evaluator_threads_manager import EvaluatorThreadsManager
from config.cst import TimeFrames
from octobot import OctoBot


def _get_tools():
    symbol = "BTC/USDT"
    exchange_traders = {}
    exchange_traders2 = {}
    config = load_test_config()
    time_frame = TimeFrames.ONE_HOUR
    AdvancedManager.create_class_list(config)
    symbol_time_frame_updater_thread = SymbolTimeFramesDataUpdaterThread()
    exchange_manager = ExchangeManager(config, ccxt.binance, is_simulated=True)
    exchange_inst = exchange_manager.get_exchange()
    trader_inst = TraderSimulator(config, exchange_inst, 0.3)
    trader_inst.stop_order_manager()
    trader_inst2 = TraderSimulator(config, exchange_inst, 0.3)
    trader_inst2.stop_order_manager()
    crypto_currency_evaluator = CryptocurrencyEvaluator(config, "Bitcoin", [])
    symbol_evaluator = SymbolEvaluator(config, symbol, crypto_currency_evaluator)
    exchange_traders[exchange_inst.get_name()] = trader_inst
    exchange_traders2[exchange_inst.get_name()] = trader_inst2
    symbol_evaluator.set_trader_simulators(exchange_traders)
    symbol_evaluator.set_traders(exchange_traders2)
    symbol_evaluator.strategies_eval_lists[exchange_inst.get_name()] = EvaluatorCreator.create_strategies_eval_list(
        config)
    trading_mode_inst = OctoBot.get_trading_mode_class(config)(config, exchange_inst)
    evaluator_thread_manager = EvaluatorThreadsManager(config, time_frame, symbol_time_frame_updater_thread,
                                                       symbol_evaluator, exchange_inst, trading_mode_inst, [])
    trader_inst.portfolio.portfolio["USDT"] = {
        Portfolio.TOTAL: 2000,
        Portfolio.AVAILABLE: 2000
    }
    symbol_evaluator.add_evaluator_thread_manager(exchange_inst, time_frame, trading_mode_inst, evaluator_thread_manager)
    return symbol_evaluator, exchange_inst, time_frame, evaluator_thread_manager


def test_init():
    symbol_evaluator, exchange_inst, time_frame, evaluator_thread_manager = _get_tools()
    assert symbol_evaluator.trading_mode_instances[exchange_inst.get_name()]
    assert symbol_evaluator.evaluator_thread_managers[exchange_inst.get_name()][time_frame] == evaluator_thread_manager
