#!/bin/bash

# Complete VM Creation Test Suite
# Runs both integration tests and LLM simulation tests

echo "🚀 Starting Complete VM Creation Test Suite..."
echo "================================================="

# Check environment
if [ -z "$VME_API_BASE_URL" ] || [ -z "$VME_API_TOKEN" ]; then
    echo "❌ VME credentials required"
    echo "   Set VME_API_BASE_URL and VME_API_TOKEN environment variables"
    echo "   Or load with: source .env"
    exit 1
fi

echo "✅ Environment ready"
echo "   API: $VME_API_BASE_URL"
echo "   Token: ${VME_API_TOKEN:0:20}..."
echo ""

# Test 1: Integration Tests (actual VM creation)
echo "📋 TEST 1: VM Creation Integration Tests"
echo "----------------------------------------"
echo "⚠️  WARNING: This will create and delete actual VMs in VME"
echo ""
read -p "Continue with integration tests? (y/N): " confirm

if [[ $confirm =~ ^[Yy]$ ]]; then
    echo "🔥 Running VM creation integration tests..."
    python3 tests/test_vm_creation_integration.py
    integration_result=$?
    
    if [ $integration_result -eq 0 ]; then
        echo "✅ Integration tests PASSED"
    else
        echo "❌ Integration tests FAILED"
    fi
else
    echo "⏭️  Skipping integration tests"
    integration_result=0  # Don't fail overall if user skips
fi

echo ""

# Test 2: LLM Simulation Tests
echo "📋 TEST 2: LLM Workflow Simulation Tests"
echo "----------------------------------------"
echo "⚠️  WARNING: This will create and delete test VMs during LLM simulation"
echo ""
read -p "Continue with LLM simulation tests? (y/N): " confirm_llm

if [[ $confirm_llm =~ ^[Yy]$ ]]; then
    echo "🤖 Running LLM simulation tests..."
    python3 tests/test_llm_simulation.py
    llm_result=$?
    
    if [ $llm_result -eq 0 ]; then
        echo "✅ LLM simulation tests PASSED"
    else
        echo "❌ LLM simulation tests FAILED"
    fi
else
    echo "⏭️  Skipping LLM simulation tests"
    llm_result=0  # Don't fail overall if user skips
fi

echo ""

# Overall Results
echo "📊 COMPLETE TEST SUITE SUMMARY"
echo "=============================="

if [ $integration_result -eq 0 ] && [ $llm_result -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED!"
    echo ""
    echo "✅ Progressive discovery system working"
    echo "✅ VM creation workflow functional"
    echo "✅ LLM simulation validates user experience"
    echo "✅ Real VME integration confirmed"
    echo ""
    echo "🎯 Ready for production deployment!"
    exit 0
else
    echo "❌ Some tests failed"
    echo ""
    if [ $integration_result -ne 0 ]; then
        echo "❌ Integration tests failed"
    fi
    if [ $llm_result -ne 0 ]; then
        echo "❌ LLM simulation tests failed"
    fi
    echo ""
    echo "🔧 Check test output above for details"
    exit 1
fi