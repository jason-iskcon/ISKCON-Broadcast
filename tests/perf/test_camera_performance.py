"""
Performance tests for camera system

Tests camera system performance including frame throughput, latency,
memory usage, and scalability under various load conditions.
"""

import pytest
import time
import threading
import psutil
import gc
from statistics import mean, median, stdev
from unittest.mock import patch, MagicMock

from src.camera_registry import CameraRegistry
from src.camera_interface import CameraInterface


class TestCameraPerformance:
    """Performance test suite for camera system"""
    
    @pytest.mark.performance
    def test_single_camera_frame_throughput(self, mock_camera_config, camera_registry_with_mocks, performance_timer):
        """Test frame throughput for single camera"""
        with performance_timer("single_camera_throughput"):
            camera = CameraRegistry.create_camera('mock', 0, mock_camera_config)
            camera.capture_frames()
            
            # Measure frame generation rate
            start_time = time.time()
            initial_frame_count = getattr(camera, 'frame_count', 0)
            
            time.sleep(2.0)  # Measure for 2 seconds
            
            final_frame_count = getattr(camera, 'frame_count', 0)
            elapsed_time = time.time() - start_time
            
            fps = (final_frame_count - initial_frame_count) / elapsed_time
            
            camera.stop()
            
            # Should achieve at least 25 FPS
            assert fps >= 25.0, f"Frame rate too low: {fps:.2f} FPS"
    
    @pytest.mark.performance
    def test_multiple_camera_throughput(self, camera_registry_with_mocks, performance_timer):
        """Test throughput with multiple cameras"""
        camera_configs = [
            {'id': i, 'type': 'mock', 'source': 'generated', 'fps': 30}
            for i in range(3)
        ]
        
        with performance_timer("multiple_camera_throughput"):
            cameras = []
            
            for config in camera_configs:
                camera = CameraRegistry.create_camera('mock', config['id'], config)
                cameras.append(camera)
                camera.capture_frames()
            
            # Let cameras run for measurement period
            time.sleep(2.0)
            
            total_fps = 0
            for camera in cameras:
                frame_count = getattr(camera, 'frame_count', 0)
                fps = frame_count / 2.0  # 2 second measurement
                total_fps += fps
                camera.stop()
            
            # Should maintain good performance with multiple cameras
            assert total_fps >= 60.0, f"Total FPS too low: {total_fps:.2f}"
    
    @pytest.mark.performance
    def test_frame_latency_measurement(self, mock_camera_config, camera_registry_with_mocks, performance_timer):
        """Test frame capture latency"""
        with performance_timer("frame_latency"):
            camera = CameraRegistry.create_camera('mock', 0, mock_camera_config)
            camera.capture_frames()
            
            # Wait for camera to start
            time.sleep(0.1)
            
            # Measure frame access latency
            latencies = []
            for _ in range(10):
                start = time.time()
                frame = camera.get_frame()
                end = time.time()
                
                if frame is not None:
                    latencies.append((end - start) * 1000)  # Convert to ms
                
                time.sleep(0.1)
            
            camera.stop()
            
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                # Frame access should be very fast (< 10ms)
                assert avg_latency < 10.0, f"Frame latency too high: {avg_latency:.2f}ms"
    
    @pytest.mark.performance
    def test_memory_usage_single_camera(self, mock_camera_config, camera_registry_with_mocks, performance_timer):
        """Test memory usage with single camera"""
        process = psutil.Process()
        
        with performance_timer("memory_single_camera"):
            # Baseline memory
            gc.collect()
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            camera = CameraRegistry.create_camera('mock', 0, mock_camera_config)
            camera.capture_frames()
            
            # Let it run and measure memory
            time.sleep(2.0)
            
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - baseline_memory
            
            camera.stop()
            
            # Memory increase should be reasonable (< 50MB for mock camera)
            assert memory_increase < 50.0, f"Memory usage too high: {memory_increase:.2f}MB"
    
    @pytest.mark.performance
    def test_memory_usage_multiple_cameras(self, camera_registry_with_mocks, performance_timer):
        """Test memory usage with multiple cameras"""
        process = psutil.Process()
        
        camera_configs = [
            {'id': i, 'type': 'mock', 'source': 'generated', 'fps': 30}
            for i in range(5)
        ]
        
        with performance_timer("memory_multiple_cameras"):
            # Baseline memory
            gc.collect()
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            cameras = []
            for config in camera_configs:
                camera = CameraRegistry.create_camera('mock', config['id'], config)
                cameras.append(camera)
                camera.capture_frames()
            
            # Let them run and measure memory
            time.sleep(2.0)
            
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - baseline_memory
            
            for camera in cameras:
                camera.stop()
            
            # Memory increase should scale reasonably (< 100MB for 5 cameras)
            assert memory_increase < 100.0, f"Memory usage too high: {memory_increase:.2f}MB"
    
    @pytest.mark.performance
    def test_cpu_usage_under_load(self, camera_registry_with_mocks, performance_timer):
        """Test CPU usage under load"""
        camera_configs = [
            {'id': i, 'type': 'mock', 'source': 'generated', 'fps': 60}
            for i in range(3)
        ]
        
        with performance_timer("cpu_usage_load"):
            cameras = []
            
            # Start monitoring CPU
            process = psutil.Process()
            cpu_percent_start = process.cpu_percent()
            
            for config in camera_configs:
                camera = CameraRegistry.create_camera('mock', config['id'], config)
                cameras.append(camera)
                camera.capture_frames()
            
            # Let cameras run under load
            time.sleep(3.0)
            
            cpu_percent_end = process.cpu_percent()
            
            for camera in cameras:
                camera.stop()
            
            # CPU usage should be reasonable (this is system dependent)
            # Just ensure it's not completely out of control
            assert cpu_percent_end < 90.0, f"CPU usage too high: {cpu_percent_end:.2f}%"
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_scalability_camera_count(self, camera_registry_with_mocks, performance_timer):
        """Test system scalability with increasing camera count"""
        max_cameras = 10
        
        with performance_timer("scalability_test"):
            for camera_count in [1, 3, 5, 7, 10]:
                cameras = []
                
                config = {'type': 'mock', 'source': 'generated', 'fps': 30}
                
                start_time = time.time()
                
                # Create and start cameras
                for i in range(camera_count):
                    camera = CameraRegistry.create_camera('mock', i, config)
                    cameras.append(camera)
                    camera.capture_frames()
                
                # Let them run briefly
                time.sleep(1.0)
                
                # Measure performance
                total_frames = sum(getattr(cam, 'frame_count', 0) for cam in cameras)
                
                # Stop all cameras
                for camera in cameras:
                    camera.stop()
                
                elapsed = time.time() - start_time
                
                # Performance should degrade gracefully
                fps_per_camera = total_frames / camera_count / elapsed if elapsed > 0 else 0
                
                # Each camera should maintain reasonable performance
                assert fps_per_camera >= 10.0, f"Performance degraded too much with {camera_count} cameras: {fps_per_camera:.2f} FPS per camera"
    
    @pytest.mark.performance
    def test_frame_generation_performance(self, camera_registry_with_mocks, performance_timer):
        """Test frame generation performance specifically"""
        config = {
            'type': 'mock',
            'source': 'generated',
            'fps': 60,
            'width': 1280,
            'height': 720
        }
        
        with performance_timer("frame_generation"):
            camera = CameraRegistry.create_camera('mock', 0, config)
            camera.capture_frames()
            
            # Let it generate frames at high resolution/fps
            time.sleep(2.0)
            
            frame_count = getattr(camera, 'frame_count', 0)
            fps = frame_count / 2.0
            
            camera.stop()
            
            # Should handle high resolution at decent frame rate
            assert fps >= 30.0, f"High resolution frame generation too slow: {fps:.2f} FPS"
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_long_term_performance_stability(self, mock_camera_config, camera_registry_with_mocks, performance_timer):
        """Test performance stability over longer period"""
        with performance_timer("long_term_stability"):
            camera = CameraRegistry.create_camera('mock', 0, mock_camera_config)
            camera.capture_frames()
            
            # Measure performance over multiple intervals
            measurements = []
            
            for interval in range(5):  # 5 intervals of 2 seconds each
                start_count = getattr(camera, 'frame_count', 0)
                time.sleep(2.0)
                end_count = getattr(camera, 'frame_count', 0)
                
                fps = (end_count - start_count) / 2.0
                measurements.append(fps)
            
            camera.stop()
            
            # Performance should be stable (variance < 20%)
            avg_fps = sum(measurements) / len(measurements)
            max_deviation = max(abs(fps - avg_fps) for fps in measurements)
            variance_percent = (max_deviation / avg_fps) * 100 if avg_fps > 0 else 0
            
            assert variance_percent < 20.0, f"Performance too unstable: {variance_percent:.2f}% variance"
    
    @pytest.mark.performance
    def test_concurrent_access_performance(self, mock_camera_config, camera_registry_with_mocks, performance_timer):
        """Test performance with concurrent frame access"""
        with performance_timer("concurrent_access"):
            camera = CameraRegistry.create_camera('mock', 0, mock_camera_config)
            camera.capture_frames()
            
            # Wait for camera to start
            time.sleep(0.1)
            
            frame_counts = []
            
            def access_frames():
                """Function to access frames from multiple threads"""
                count = 0
                for _ in range(50):
                    frame = camera.get_frame()
                    if frame is not None:
                        count += 1
                    time.sleep(0.01)
                frame_counts.append(count)
            
            # Start multiple threads accessing frames
            threads = []
            for _ in range(3):
                thread = threading.Thread(target=access_frames)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            camera.stop()
            
            # All threads should successfully access frames
            total_accesses = sum(frame_counts)
            assert total_accesses > 100, f"Concurrent access failed: {total_accesses} total frame accesses" 