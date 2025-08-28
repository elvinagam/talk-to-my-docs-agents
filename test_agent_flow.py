#!/usr/bin/env python3
"""
Test the full agent flow from UI to NVIDIA data analysis
"""
import requests
import json
import time

def test_agent_flow():
    """Test the complete agent flow with the question about BUF vs RSF variance."""
    
    base_url = "http://localhost:8080"
    
    print("🧪 Testing Complete Agent Flow: UI → Agent → NVIDIA Data")
    print("=" * 60)
    
    # Test 1: Test the individual API endpoints first
    print("\n📊 STEP 1: Testing Direct API Endpoints")
    
    try:
        # Test forecast summary
        response = requests.get(f"{base_url}/api/v1/forecast/summary")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Forecast Summary API: ${data['forecast_metrics']['total_rsf_revenue']:,.2f} RSF revenue")
        else:
            print(f"❌ Forecast Summary API failed: {response.status_code}")
            return
    
    except Exception as e:
        print(f"❌ Error testing forecast API: {e}")
        return
    
    # Test 2: Test the agent chat endpoint with our question
    print("\n🤖 STEP 2: Testing Agent Chat Endpoint")
    
    try:
        # Create a chat completion request like the UI would send
        chat_data = {
            "model": "datarobot/azure/gpt-4o-mini",  # The LLM model
            "messages": [
                {
                    "role": "user",
                    "content": "What accounts have the highest BUF vs RSF variance?"
                }
            ],
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        print(f"🔄 Sending query: '{chat_data['messages'][0]['content']}'")
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/v1/chat/agent/completions",
            json=chat_data,
            headers=headers,
            timeout=120  # 2 minute timeout for agent processing
        )
        end_time = time.time()
        
        print(f"⏱️  Response time: {end_time - start_time:.1f} seconds")
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                answer = result["choices"][0]["message"]["content"]
                print(f"\n✅ AGENT RESPONSE RECEIVED:")
                print("=" * 50)
                print(answer)
                print("=" * 50)
                
                # Check if the answer contains real data insights
                if "variance" in answer.lower():
                    print(f"\n🎯 SUCCESS: Agent provided variance analysis!")
                elif "error" in answer.lower() or "unavailable" in answer.lower():
                    print(f"\n⚠️  PARTIAL: Agent couldn't access forecast data")
                else:
                    print(f"\n✅ RESPONSE: Agent provided an answer")
            else:
                print(f"❌ No valid response in chat completion")
                
        else:
            print(f"❌ Agent request failed: {response.status_code}")
            print(f"Response: {response.text}")
        
    except requests.exceptions.Timeout:
        print(f"⏰ Agent request timed out after 2 minutes")
    except Exception as e:
        print(f"❌ Error testing agent: {e}")
    
    # Test 3: Test specific account query
    print(f"\n🏢 STEP 3: Testing Specific Account Analysis")
    
    try:
        account_response = requests.get(f"{base_url}/api/v1/forecast/account/MICROSOFT/variance?period=current")
        if account_response.status_code == 200:
            account_data = account_response.json()
            print(f"✅ Microsoft Account Analysis: {account_data}")
        else:
            print(f"⚠️  Account endpoint returned: {account_response.status_code}")
    except Exception as e:
        print(f"❌ Error testing account endpoint: {e}")
    
    print(f"\n🏁 TESTING COMPLETE")

if __name__ == "__main__":
    test_agent_flow()
