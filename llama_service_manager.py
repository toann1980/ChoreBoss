#!/usr/bin/env python3
"""
Llama Service Manager - Start/stop services and run benchmarks
"""

import subprocess
import time
import sys
import json
import requests

class LlamaServiceManager:
    def __init__(self):
        self.services = {
            "phi": {"port": 11436, "name": "llama-phi.service"},
            "mistral": {"port": 11437, "name": "llama-mistral.service"},
            "hermes": {"port": 11438, "name": "llama-hermes.service"},
            "nemotron": {"port": 11439, "name": "llama-nemotron.service"},
            "gemma4-q3": {"port": 11440, "name": "llama-gemma4-q3.service"},
            "gemma4-iq3": {"port": 11441, "name": "llama-gemma4-iq3.service"},
        }
    
    def run_cmd(self, cmd, sudo=True):
        """Run shell command"""
        if sudo:
            cmd = f"sudo {cmd}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timeout"
    
    def start_service(self, model_name):
        """Start a single service"""
        if model_name not in self.services:
            print(f"❌ Unknown model: {model_name}")
            return False
        
        service = self.services[model_name]
        print(f"Starting {model_name} ({service['name']})...")
        
        code, out, err = self.run_cmd(f"systemctl start {service['name']}")
        if code == 0:
            print(f"✅ Started")
            # Wait for service to be ready
            time.sleep(3)
            return True
        else:
            print(f"❌ Failed: {err}")
            return False
    
    def stop_service(self, model_name):
        """Stop a service"""
        if model_name not in self.services:
            print(f"❌ Unknown model: {model_name}")
            return False
        
        service = self.services[model_name]
        print(f"Stopping {model_name}...")
        
        code, out, err = self.run_cmd(f"systemctl stop {service['name']}")
        if code == 0:
            print(f"✅ Stopped")
            time.sleep(2)
            return True
        else:
            print(f"❌ Failed: {err}")
            return False
    
    def status(self):
        """Show all service status"""
        print("\n" + "="*70)
        print("LLAMA SERVICE STATUS")
        print("="*70)
        
        for model, info in self.services.items():
            code, out, err = self.run_cmd(f"systemctl is-active {info['name']}", sudo=True)
            is_running = "running" in out.lower()
            status = "🟢 RUNNING" if is_running else "⚫ STOPPED"
            print(f"{model:15} {status:15} Port {info['port']}")
    
    def test_port(self, port, timeout=5):
        """Test if port is responding"""
        try:
            response = requests.post(
                f"http://localhost:{port}/v1/chat/completions",
                json={"messages": [{"role": "user", "content": "test"}], "max_tokens": 5},
                timeout=timeout
            )
            return response.status_code == 200
        except:
            return False
    
    def benchmark_model(self, model_name, num_tests=5):
        """Run benchmark on a model"""
        if model_name not in self.services:
            print(f"❌ Unknown model: {model_name}")
            return None
        
        port = self.services[model_name]["port"]
        url = f"http://localhost:{port}/v1/chat/completions"
        
        print(f"\n{'='*70}")
        print(f"BENCHMARKING: {model_name} (Port {port})")
        print(f"{'='*70}\n")
        
        # Check connectivity
        print("Checking connectivity...")
        max_wait = 30
        for i in range(max_wait):
            if self.test_port(port, timeout=2):
                print(f"✅ Connected\n")
                break
            print(f"  Waiting... ({i+1}/{max_wait}s)")
            time.sleep(1)
        else:
            print(f"❌ Could not connect to port {port}")
            return None
        
        # Warmup
        print("Warmup (3 requests, discarded):")
        for i in range(3):
            try:
                start = time.time()
                r = requests.post(
                    url,
                    json={"messages": [{"role": "user", "content": "test"}], "max_tokens": 100},
                    timeout=30
                )
                elapsed = time.time() - start
                if r.status_code == 200:
                    tokens = r.json().get("usage", {}).get("completion_tokens", 0)
                    print(f"  {i+1}: {elapsed:.2f}s, {tokens} tokens")
            except Exception as e:
                print(f"  {i+1}: Error - {type(e).__name__}")
            time.sleep(0.5)
        
        # Measurement
        print("\nMeasurement (5 requests, recorded):")
        results = []
        for i in range(num_tests):
            try:
                start = time.time()
                r = requests.post(
                    url,
                    json={"messages": [{"role": "user", "content": "What is 2+2?"}], "max_tokens": 100},
                    timeout=30
                )
                elapsed = time.time() - start
                
                if r.status_code == 200:
                    data = r.json()
                    tokens = data.get("usage", {}).get("completion_tokens", 0)
                    tok_per_sec = tokens / elapsed if elapsed > 0 else 0
                    results.append({"latency": elapsed, "tokens": tokens, "tok_per_sec": tok_per_sec})
                    print(f"  {i+1}: {elapsed:.2f}s, {tokens} tokens, {tok_per_sec:.1f} tok/s ✅")
            except Exception as e:
                print(f"  {i+1}: {type(e).__name__}")
            time.sleep(0.5)
        
        # Summary
        if results:
            latencies = [r["latency"] for r in results]
            tokens_list = [r["tokens"] for r in results]
            tok_per_secs = [r["tok_per_sec"] for r in results]
            
            avg_latency = sum(latencies) / len(latencies)
            avg_tokens = sum(tokens_list) / len(tokens_list)
            avg_tok_per_sec = sum(tok_per_secs) / len(tok_per_secs)
            
            print(f"\nRESULTS:")
            print(f"  Latency: {avg_latency:.2f}s")
            print(f"  Tokens: {avg_tokens:.0f}")
            print(f"  Tok/s: {avg_tok_per_sec:.1f} ✅")
            
            return {
                "model": model_name,
                "port": port,
                "avg_latency": avg_latency,
                "avg_tokens": avg_tokens,
                "avg_tok_per_sec": avg_tok_per_sec,
                "tests": len(results)
            }
        else:
            print(f"\nRESULTS: ❌ NO DATA")
            return None
    
    def cycle_benchmark(self, models_to_test):
        """Benchmark multiple models sequentially"""
        results = []
        
        for model in models_to_test:
            # Stop all other services
            print(f"\n{'='*70}")
            print(f"Preparing {model}...")
            print(f"{'='*70}\n")
            
            self.stop_all_except(model)
            
            # Start the model
            if self.start_service(model):
                # Run benchmark
                result = self.benchmark_model(model)
                if result:
                    results.append(result)
            
            # Stop the service
            self.stop_service(model)
            time.sleep(2)
        
        # Summary
        if results:
            print(f"\n{'='*70}")
            print("BENCHMARK SUMMARY - All Models")
            print(f"{'='*70}\n")
            
            print(f"{'Model':<20} {'Latency':<12} {'Tok/s':<10}")
            print("-"*50)
            
            for result in sorted(results, key=lambda x: x["avg_tok_per_sec"], reverse=True):
                model = result["model"]
                latency = f"{result['avg_latency']:.2f}s"
                tok_s = f"{result['avg_tok_per_sec']:.1f}"
                print(f"{model:<20} {latency:<12} {tok_s:<10}")
            
            # Save results
            with open("/tmp/llama_benchmark_results.json", "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n✅ Results saved to /tmp/llama_benchmark_results.json")
    
    def stop_all_except(self, keep_model):
        """Stop all services except one"""
        for model in self.services:
            if model != keep_model:
                code, _, _ = self.run_cmd(f"systemctl is-active {self.services[model]['name']}", sudo=True)
                if code == 0:  # Service is running
                    self.stop_service(model)

def main():
    manager = LlamaServiceManager()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 llama_service_manager.py status")
        print("  python3 llama_service_manager.py start <model>")
        print("  python3 llama_service_manager.py stop <model>")
        print("  python3 llama_service_manager.py benchmark <model>")
        print("  python3 llama_service_manager.py cycle <model1> <model2> ...")
        print("")
        print("Models: phi, mistral, hermes, nemotron, gemma4-q3, gemma4-iq3")
        print("")
        manager.status()
        return
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        manager.status()
    elif cmd == "start" and len(sys.argv) > 2:
        manager.start_service(sys.argv[2])
    elif cmd == "stop" and len(sys.argv) > 2:
        manager.stop_service(sys.argv[2])
    elif cmd == "benchmark" and len(sys.argv) > 2:
        manager.benchmark_model(sys.argv[2])
    elif cmd == "cycle" and len(sys.argv) > 2:
        models = sys.argv[2:]
        manager.cycle_benchmark(models)
    else:
        print(f"❌ Unknown command: {cmd}")

if __name__ == "__main__":
    main()
