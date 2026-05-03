#!/usr/bin/env python3
"""
Comprehensive Model Benchmark Suite
Tests embedding models and inference models systematically
"""

import subprocess
import time
import sys
import json
import requests
from typing import Optional, Dict, Any, List

class ComprehensiveModelBenchmark:
    def __init__(self):
        # Embedding models (port 11434-11436)
        self.embedding_models = {
            "nomic-q8": {
                "port": 11434,
                "model": "/home/leto/.openclaw/models/gguf/nomic-embed-text-v1.5.Q8_0.gguf",
                "service": "llama-embedding-q8",
                "size": "140MB",
                "type": "embedding"
            },
            "nomic-f16": {
                "port": 11435,
                "model": "/home/leto/.openclaw/models/gguf/nomic-embed-text-v1.5.f16.gguf",
                "service": "llama-embedding-f16",
                "size": "262MB",
                "type": "embedding"
            },
            "nomic-f32": {
                "port": 11436,
                "model": "/home/leto/.openclaw/models/gguf/nomic-embed-text-v1.5.f32.gguf",
                "service": "llama-embedding-f32",
                "size": "523MB",
                "type": "embedding"
            }
        }
        
        # Inference models (port 11440-11448)
        self.inference_models = {
            "phi": {
                "port": 11440,
                "model": "/home/leto/.openclaw/models/gguf/Phi-3.5-mini-instruct-Q4_K_M.gguf",
                "service": "llama-phi",
                "size": "2.3GB",
                "temp": 0.3,
                "type": "inference"
            },
            "cq-gemma4-e2b": {
                "port": 11441,
                "model": "/home/leto/.openclaw/models/gguf/CQ-Gemma-4-E2B-bF16-Q4_K.gguf",
                "service": "llama-cq-gemma4-e2b",
                "size": "3.2GB",
                "temp": 1.0,
                "type": "inference"
            },
            "gemma4-e4b-iq2": {
                "port": 11442,
                "model": "/home/leto/.openclaw/models/gguf/gemma-4-E4B-it-UD-IQ2_M_unsloth.gguf",
                "service": "llama-gemma4-e4b-iq2",
                "size": "3.3GB",
                "temp": 1.0,
                "type": "inference"
            },
            "gemma4-e2b-q5s": {
                "port": 11443,
                "model": "/home/leto/.openclaw/models/gguf/google_gemma-4-E2B-it-Q5_K_S.gguf",
                "service": "llama-gemma4-e2b-q5s",
                "size": "3.4GB",
                "temp": 1.0,
                "type": "inference"
            },
            "gemma4-e2b-q5m": {
                "port": 11444,
                "model": "/home/leto/.openclaw/models/gguf/google_gemma-4-E2B-it-Q5_K_M.gguf",
                "service": "llama-gemma4-e2b-q5m",
                "size": "3.5GB",
                "temp": 1.0,
                "type": "inference"
            },
            "gemma4-e4b-iq3": {
                "port": 11445,
                "model": "/home/leto/.openclaw/models/gguf/gemma-4-E4B-it-UD-IQ3_XXS_unsloth.gguf",
                "service": "llama-gemma4-e4b-iq3",
                "size": "3.5GB",
                "temp": 1.0,
                "type": "inference"
            },
            "gemma4-e4b-q2xl": {
                "port": 11446,
                "model": "/home/leto/.openclaw/models/gguf/gemma-4-E4B-it-UD-Q2_K_XL_unsloth.gguf",
                "service": "llama-gemma4-e4b-q2xl",
                "size": "3.5GB",
                "temp": 1.0,
                "type": "inference"
            }
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
    
    def benchmark_embedding(self, model_name: str, model_info: Dict) -> Optional[Dict]:
        """Benchmark embedding model"""
        port = model_info["port"]
        url = f"http://localhost:{port}/v1/embeddings"
        
        print(f"\n{'='*70}")
        print(f"BENCHMARKING EMBEDDING: {model_name} (Port {port})")
        print(f"{'='*70}\n")
        
        # Start service
        print(f"Starting service...")
        self.run_cmd(f"systemctl start {model_info['service']}")
        time.sleep(3)
        
        # Test connectivity
        print("Testing connectivity...")
        for i in range(20):
            try:
                response = requests.post(
                    url,
                    json={"model": "nomic", "input": "test"},
                    timeout=5
                )
                if response.status_code == 200:
                    print("✅ Connected\n")
                    break
            except:
                pass
            if i > 0 and i % 5 == 0:
                print(f"  Waiting... ({i}s)")
            time.sleep(1)
        else:
            print("❌ Failed to connect")
            self.run_cmd(f"systemctl stop {model_info['service']}")
            return None
        
        # Benchmark
        print("Benchmark (10 requests, 100 tokens each):")
        times = []
        for i in range(10):
            try:
                # Create diverse test sentences
                texts = [f"Test embedding {i}: " + "Hello world. " * 10]
                
                start = time.time()
                response = requests.post(
                    url,
                    json={"model": "nomic", "input": texts},
                    timeout=30
                )
                elapsed = time.time() - start
                
                if response.status_code == 200:
                    data = response.json()
                    dims = len(data["data"][0]["embedding"])
                    times.append(elapsed)
                    print(f"  {i+1}: {elapsed:.2f}s, {dims} dims")
                else:
                    print(f"  {i+1}: HTTP {response.status_code}")
            except Exception as e:
                print(f"  {i+1}: {type(e).__name__}")
            time.sleep(0.5)
        
        # Stop service
        self.run_cmd(f"systemctl stop {model_info['service']}")
        time.sleep(2)
        
        if times:
            avg_time = sum(times) / len(times)
            print(f"\nRESULTS:")
            print(f"  Avg latency: {avg_time:.3f}s")
            print(f"  Throughput: {1/avg_time:.1f} requests/sec")
            
            return {
                "model": model_name,
                "port": port,
                "size": model_info["size"],
                "avg_latency": avg_time,
                "throughput_rps": 1/avg_time,
                "dimensions": dims
            }
        return None
    
    def benchmark_inference(self, model_name: str, model_info: Dict) -> Optional[Dict]:
        """Benchmark inference model"""
        port = model_info["port"]
        url = f"http://localhost:{port}/v1/chat/completions"
        
        print(f"\n{'='*70}")
        print(f"BENCHMARKING INFERENCE: {model_name} (Port {port})")
        print(f"{'='*70}\n")
        
        # Start service
        print(f"Starting service...")
        self.run_cmd(f"systemctl start {model_info['service']}")
        time.sleep(3)
        
        # Test connectivity
        print("Testing connectivity...")
        for i in range(20):
            try:
                response = requests.post(
                    url,
                    json={"messages": [{"role": "user", "content": "test"}], "max_tokens": 10},
                    timeout=5
                )
                if response.status_code == 200:
                    print("✅ Connected\n")
                    break
            except:
                pass
            if i > 0 and i % 5 == 0:
                print(f"  Waiting... ({i}s)")
            time.sleep(1)
        else:
            print("❌ Failed to connect")
            self.run_cmd(f"systemctl stop {model_info['service']}")
            return None
        
        # Benchmark
        print("Benchmark (5 requests, max 100 tokens):")
        results = []
        for i in range(5):
            try:
                start = time.time()
                response = requests.post(
                    url,
                    json={"messages": [{"role": "user", "content": "What is 2+2?"}], "max_tokens": 100},
                    timeout=30
                )
                elapsed = time.time() - start
                
                if response.status_code == 200:
                    data = response.json()
                    tokens = data.get("usage", {}).get("completion_tokens", 0)
                    tok_per_sec = tokens / elapsed if elapsed > 0 else 0
                    results.append({"latency": elapsed, "tokens": tokens, "tok_per_sec": tok_per_sec})
                    print(f"  {i+1}: {elapsed:.2f}s, {tokens} tokens, {tok_per_sec:.1f} tok/s")
                else:
                    print(f"  {i+1}: HTTP {response.status_code}")
            except Exception as e:
                print(f"  {i+1}: {type(e).__name__}")
            time.sleep(0.5)
        
        # Stop service
        self.run_cmd(f"systemctl stop {model_info['service']}")
        time.sleep(2)
        
        if results:
            latencies = [r["latency"] for r in results]
            tokens_list = [r["tokens"] for r in results]
            tok_per_secs = [r["tok_per_sec"] for r in results]
            
            avg_latency = sum(latencies) / len(latencies)
            avg_tokens = sum(tokens_list) / len(tokens_list)
            avg_tok_per_sec = sum(tok_per_secs) / len(tok_per_secs)
            
            print(f"\nRESULTS:")
            print(f"  Avg latency: {avg_latency:.2f}s")
            print(f"  Avg tokens: {avg_tokens:.0f}")
            print(f"  Tok/s: {avg_tok_per_sec:.1f}")
            
            return {
                "model": model_name,
                "port": port,
                "size": model_info["size"],
                "avg_latency": avg_latency,
                "avg_tokens": avg_tokens,
                "avg_tok_per_sec": avg_tok_per_sec
            }
        return None

# Run benchmarks
if __name__ == "__main__":
    bench = ComprehensiveModelBenchmark()
    
    print("="*70)
    print("COMPREHENSIVE MODEL BENCHMARK SUITE")
    print("="*70)
    
    # Note: This is a template - actual benchmarking requires service files created first
    print("\nTo run benchmarks:")
    print("1. Create systemd service files")
    print("2. Configure passwordless sudo")
    print("3. Run this benchmark suite")
