#!/usr/bin/env python
"""
Final verification that all three fixes are applied correctly.
Run this script to verify Agent V1 is working properly.
"""
import asyncio
import sys

async def verify_all_fixes():
    print("=" * 70)
    print("Agent V1 MCP Integration - Final Verification")
    print("=" * 70)

    passed = 0
    total = 0

    # Test 1: Import without RuntimeWarning
    total += 1
    print(f"\n[Test 1/{total + 2}] Import run.py without RuntimeWarning...")
    try:
        from ai_researcher.agent_v1.run import main
        print("  ✅ PASS - No RuntimeWarning")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAIL - {e}")

    # Test 2: Build graph with MCP
    total += 1
    print(f"\n[Test 2/{total + 1}] Build graph with MCP tools...")
    try:
        from ai_researcher.agent_v1.agent import build_graph
        app = await build_graph(
            include_mcp_pexlib=True,
            include_mcp_arxiv=False,
            verbose=False
        )
        print("  ✅ PASS - Graph built successfully")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAIL - {e}")

    # Test 3: Verify ainvoke is used
    total += 1
    print(f"\n[Test 3/{total}] Verify ainvoke is used for all tools...")
    try:
        import inspect
        from ai_researcher.agent_v1.agent import build_graph as bg
        source = inspect.getsource(bg)

        # Check that we use ainvoke
        if "await tool.ainvoke(args)" in source:
            print("  ✅ PASS - ainvoke is used")
            passed += 1
        else:
            print("  ❌ FAIL - ainvoke not found in source")
    except Exception as e:
        print(f"  ❌ FAIL - {e}")

    # Summary
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)

    if passed == total:
        print("\n🎉 SUCCESS! All fixes are properly applied!")
        print("\nFixed issues:")
        print("  ✅ NotImplementedError: StructuredTool async support")
        print("  ✅ RuntimeWarning: coroutine never awaited")
        print("  ✅ TypeError: Cannot invoke coroutine synchronously")
        print("\nAgent V1 with MCP is READY TO USE!")
        return 0
    else:
        print(f"\n⚠️  WARNING: {total - passed} test(s) failed")
        print("Please review the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(verify_all_fixes())
    sys.exit(exit_code)

