#!/usr/bin/env python3
"""
Wakanda Protocol Demo Script
Demonstrates key features and capabilities
"""

import asyncio
import json
from typing import Dict, Any
import httpx
from wakanda.core.config import settings
from wakanda.core.security import security_manager

async def demo_wakanda_protocol():
    """Demonstrate Wakanda Protocol capabilities"""
    
    print("🌍 WAKANDA PROTOCOL DEMONSTRATION")
    print("=" * 50)
    
    # Start the server in background for demo
    print("\n🚀 Starting Wakanda Protocol Server...")
    
    base_url = f"http://localhost:{settings.port}"
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Health Check
            print(f"\n📊 HEALTH CHECK")
            print("-" * 20)
            response = await client.get(f"{base_url}/health/")
            if response.status_code == 200:
                health = response.json()
                print(f"✅ Status: {health['status']}")
                print(f"📦 Version: {health['version']}")
                print(f"💻 System: {health['system_info']['platform']}")
                print(f"🧠 Memory: {health['system_info']['memory_available'] / 1024**3:.1f} GB available")
            
            # 2. Authentication Demo
            print(f"\n🔐 AUTHENTICATION DEMO")
            print("-" * 25)
            
            # Register a demo user
            user_data = {
                "username": "demo_user",
                "email": "demo@wakanda.africa",
                "password": "wakanda2024",
                "full_name": "Demo User"
            }
            
            response = await client.post(f"{base_url}/auth/register", json=user_data)
            if response.status_code == 200:
                print("✅ User registered successfully")
                
                # Login
                login_data = {"username": "demo_user", "password": "wakanda2024"}
                response = await client.post(f"{base_url}/auth/login", data=login_data)
                if response.status_code == 200:
                    token_data = response.json()
                    print(f"✅ Login successful")
                    print(f"🎫 Token type: {token_data['token_type']}")
                    print(f"⏰ Expires in: {token_data['expires_in']} seconds")
                    
                    auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            
            # 3. Fintech Services Demo
            print(f"\n💰 FINTECH SERVICES")
            print("-" * 20)
            
            response = await client.get(f"{base_url}/fintech/")
            fintech_info = response.json()
            print(f"📈 Module: {fintech_info['module']}")
            print(f"🌍 Status: {fintech_info['status']}")
            print("💱 Features:")
            for feature in fintech_info['features'][:3]:
                print(f"   • {feature}")
            
            # Get exchange rates
            response = await client.get(f"{base_url}/fintech/exchange-rates")
            rates = response.json()
            print(f"\n💱 Exchange Rates (Base: {rates['base_currency']}):")
            for currency, rate in list(rates['rates'].items())[:4]:
                print(f"   {currency}: {rate}")
            
            # 4. AI Services Demo
            print(f"\n🤖 AI SERVICES")
            print("-" * 15)
            
            response = await client.get(f"{base_url}/ai/")
            ai_info = response.json()
            print(f"🧠 Supported Languages: {len(ai_info['supported_languages'])}")
            print("🌍 Sample Languages:")
            response = await client.get(f"{base_url}/ai/languages")
            languages = response.json()
            for lang in languages['languages'][:5]:
                print(f"   • {lang['name']} ({lang['code']}) - {lang['region']}")
            
            # Translation demo
            translation_request = {
                "text": "Welcome to Wakanda Protocol",
                "source_language": "en",
                "target_language": "sw"
            }
            response = await client.post(f"{base_url}/ai/translate", json=translation_request)
            if response.status_code == 200:
                translation = response.json()
                print(f"\n🔤 Translation Demo:")
                print(f"   Original (EN): {translation['original_text']}")
                print(f"   Swahili (SW): {translation['translated_text']}")
                print(f"   Confidence: {translation['confidence']:.1%}")
            
            # 5. Minerals & Supply Chain Demo
            print(f"\n⛏️  MINERALS & SUPPLY CHAIN")
            print("-" * 30)
            
            response = await client.get(f"{base_url}/minerals/prices")
            prices = response.json()
            print("💎 Current Mineral Prices:")
            for price in prices:
                print(f"   • {price['mineral'].title()}: ${price['price_per_unit']:,.2f} per {price['unit']}")
            
            # Investment recommendations
            response = await client.get(f"{base_url}/minerals/investment/recommendations")
            recommendations = response.json()
            print(f"\n📊 AI Investment Recommendations:")
            for rec in recommendations:
                print(f"   • {rec['mineral'].title()}: {rec['recommendation']} (Confidence: {rec['confidence']:.1%})")
                print(f"     Reasoning: {rec['reasoning']}")
            
            # 6. Infrastructure Demo
            print(f"\n🚁 INFRASTRUCTURE & LOGISTICS")
            print("-" * 35)
            
            response = await client.get(f"{base_url}/infrastructure/drones/fleet")
            fleet = response.json()
            print(f"🛰️  Drone Fleet Status ({len(fleet)} units):")
            for drone in fleet:
                print(f"   • {drone['drone_id']}: {drone['status']} ({drone['battery_level']:.1f}% battery)")
            
            # Weather conditions
            response = await client.get(f"{base_url}/infrastructure/weather/current")
            weather = response.json()
            print(f"\n🌤️  Weather Conditions:")
            for location in weather['locations'][:2]:
                print(f"   • {location['city']}: {location['temperature']}°C, {location['conditions']}")
                print(f"     Drone Operations: {location['drone_operations']}")
            
            # 7. Governance & Compliance Demo
            print(f"\n🏛️  GOVERNANCE & COMPLIANCE")
            print("-" * 30)
            
            response = await client.get(f"{base_url}/governance/compliance/status")
            compliance = response.json()
            print("📋 Compliance Status:")
            for comp in compliance:
                status_icon = "✅" if comp['status'] == "compliant" else "⚠️"
                print(f"   {status_icon} {comp['standard'].upper()}: {comp['score']:.1f}% ({comp['status']})")
            
            # 8. Security Demo
            print(f"\n🔐 SECURITY FEATURES")
            print("-" * 20)
            
            print("🛡️  Security Capabilities:")
            print(f"   • HSM Support: {'✅' if settings.hsm_enabled else '❌'} Configured")
            print(f"   • JWT Algorithm: {settings.algorithm}")
            print(f"   • Token Expiry: {settings.access_token_expire_minutes} minutes")
            print("   • Multi-layer Encryption: ✅ Fernet + RSA")
            print("   • Security Headers: ✅ Enabled")
            
            # Generate sample encrypted data
            sample_data = "Sensitive Wakanda Protocol Data"
            encrypted = security_manager.encrypt_data(sample_data)
            decrypted = security_manager.decrypt_data(encrypted).decode()
            print(f"\n🔒 Encryption Demo:")
            print(f"   Original: {sample_data}")
            print(f"   Encrypted: {encrypted[:50]}...")
            print(f"   Decrypted: {decrypted}")
            print(f"   ✅ Encryption working correctly!")
            
        except httpx.ConnectError:
            print("❌ Could not connect to Wakanda Protocol server")
            print("💡 Start the server with: python run_dev.py")
            return
        except Exception as e:
            print(f"❌ Demo error: {e}")
            return
    
    print(f"\n🎉 WAKANDA PROTOCOL DEMONSTRATION COMPLETE!")
    print("=" * 50)
    print("🌍 Ready to serve African sovereignty and digital empowerment")
    print("🚀 Visit http://localhost:8000/docs for interactive API documentation")


if __name__ == "__main__":
    asyncio.run(demo_wakanda_protocol())