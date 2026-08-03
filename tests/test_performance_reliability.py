"""
Comprehensive Unit & Integration Test Suite for Performance, Reliability & Production Readiness Platform.
"""

import pytest
import time
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.models.benchmark_result import BenchmarkResult
from app.models.resource_snapshot import ResourceSnapshot
from app.models.performance_report import PerformanceReport

from app.performance.latency_analyzer import LatencyAnalyzer
from app.performance.cache_manager import CacheManager, LRUCache
from app.performance.memory_optimizer import MemoryOptimizer
from app.performance.resource_monitor import ResourceMonitor
from app.performance.benchmark_runner import BenchmarkRunner
from app.performance.load_tester import LoadTester

from app.reliability.circuit_breaker import CircuitBreaker, CircuitState
from app.reliability.rate_limiter import RateLimiter
from app.reliability.health_recovery import HealthRecoveryEngine
from app.reliability.graceful_shutdown import GracefulShutdownManager
from app.reliability.backup_manager import BackupManager

from app.services.performance_service import PerformanceService
from app.api.performance_api import router as performance_router


class TestLatencyAndCaching:
    """Tests latency percentiles and LRU caching mechanisms."""

    def test_latency_analyzer_percentiles(self):
        analyzer = LatencyAnalyzer()
        latencies = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
        stats = analyzer.analyze_latencies(latencies)
        assert stats["avg"] == 55.0
        assert stats["p50"] == 60.0
        assert stats["ops_per_sec"] > 0

    def test_lru_cache_eviction_and_hits(self):
        cache = LRUCache(capacity=2)
        cache.set("a", 1)
        cache.set("b", 2)

        assert cache.get("a") == 1
        assert cache.hits == 1

        # Insert 'c', evicting least recently used 'b'
        cache.set("c", 3)
        assert cache.get("b") is None
        assert cache.misses == 1

    def test_cache_manager(self):
        cm = CacheManager()
        cm.set_prompt("Who are you?", "Astra OS")
        assert cm.get_prompt("Who are you?") == "Astra OS"

        stats = cm.get_stats()
        assert stats["prompt_cache_size"] == 1
        assert stats["prompt_cache_hits"] == 1

        cm.clear_all()
        assert cm.get_prompt("Who are you?") is None


class TestResourceMonitoringAndMemory:
    """Tests resource monitoring and memory optimization."""

    def test_resource_monitor(self):
        monitor = ResourceMonitor()
        snapshot = monitor.harvest_snapshot(queue_size=3)
        assert snapshot.ram_used_mb > 0
        assert snapshot.disk_percent >= 0
        assert snapshot.active_threads >= 1
        assert snapshot.queue_size == 3

    def test_memory_optimizer(self):
        cm = CacheManager()
        opt = MemoryOptimizer(cm)
        res = opt.optimize_memory()
        assert "unreachable_objects_collected" in res
        assert res["memory_after_mb"] > 0


class TestReliabilityPatterns:
    """Tests Circuit Breaker, Rate Limiter, Shutdown Hooks, and Health Recovery."""

    def test_circuit_breaker_state_transitions(self):
        cb = CircuitBreaker(name="test_api", failure_threshold=2, recovery_timeout=0.2)
        assert cb.state == CircuitState.CLOSED

        def failing_fn():
            raise ValueError("API Failure")

        # 1st failure
        with pytest.raises(ValueError):
            cb.call(failing_fn)
        assert cb.state == CircuitState.CLOSED

        # 2nd failure -> Trips OPEN
        with pytest.raises(ValueError):
            cb.call(failing_fn)
        assert cb.state == CircuitState.OPEN

        # Next call while OPEN -> Rejects with RuntimeError immediately
        with pytest.raises(RuntimeError) as exc_info:
            cb.call(lambda: "ok")
        assert "is OPEN" in str(exc_info.value)

        # Wait for recovery timeout -> Transitions to HALF_OPEN -> SUCCESS -> CLOSED
        time.sleep(0.25)
        success_res = cb.call(lambda: "recovered")
        assert success_res == "recovered"
        assert cb.state == CircuitState.CLOSED

    def test_rate_limiter(self):
        limiter = RateLimiter(max_tokens=2, refill_rate_per_sec=1.0)
        assert limiter.acquire(1) is True
        assert limiter.acquire(1) is True
        assert limiter.acquire(1) is False  # Throttled

    def test_graceful_shutdown(self):
        mgr = GracefulShutdownManager()
        flag = {"cleaned": False}

        def cleanup_hook():
            flag["cleaned"] = True

        mgr.register_shutdown_hook(cleanup_hook)
        res = mgr.trigger_graceful_shutdown()
        assert res["status"] == "shutdown_complete"
        assert res["hooks_executed"] == 1
        assert flag["cleaned"] is True

    def test_health_recovery_checkpoint(self, tmp_path):
        chk_file = str(tmp_path / "checkpoint.json")
        engine = HealthRecoveryEngine(checkpoint_path=chk_file)
        state = {"active_task": "task_101", "status": "running"}

        assert engine.save_checkpoint(state) is True
        recovered = engine.recover_last_checkpoint()
        assert recovered == state


class TestBenchmarkAndLoadTesting:
    """Tests benchmark runner, load tester, and Master Performance Service."""

    def test_benchmark_runner(self):
        runner = BenchmarkRunner()
        res = runner.run_benchmark("test_subsystem", lambda: time.sleep(0.001), samples=5)
        assert res.subsystem == "test_subsystem"
        assert res.sample_count == 5
        assert res.avg_latency_ms > 0

    def test_load_tester(self):
        tester = LoadTester()
        res = tester.run_concurrent_load_test(lambda: time.sleep(0.001), concurrent_workers=2, total_tasks=5)
        assert res["success_count"] == 5
        assert res["failure_count"] == 0

    def test_performance_service_report(self):
        svc = PerformanceService()
        report = svc.generate_performance_report(samples=2)
        assert "planner_agent" in report.benchmarks
        assert report.resource_snapshot is not None
        assert len(report.recommendations) >= 1


class TestPerformanceAPIEndpoints:
    """Tests FastAPI Performance Router REST endpoints."""

    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(performance_router)
        self.client = TestClient(self.app)

    def test_performance_report_endpoint(self):
        res = self.client.get("/api/performance/report?samples=2")
        assert res.status_code == 200
        assert "report_id" in res.json()

    def test_resources_endpoint(self):
        res = self.client.get("/api/performance/resources")
        assert res.status_code == 200
        assert "cpu_percent" in res.json()

    def test_load_test_endpoint(self):
        res = self.client.post("/api/performance/load-test", json={"workers": 2, "tasks": 4})
        assert res.status_code == 200
        assert res.json()["success_count"] == 4

    def test_cache_endpoints(self):
        res_get = self.client.get("/api/performance/cache")
        assert res_get.status_code == 200

        res_clear = self.client.post("/api/performance/cache/clear")
        assert res_clear.status_code == 200
        assert res_clear.json()["status"] == "cache_cleared"

    def test_circuit_breakers_endpoint(self):
        res = self.client.get("/api/reliability/circuit-breakers")
        assert res.status_code == 200
        assert "openai" in res.json()
