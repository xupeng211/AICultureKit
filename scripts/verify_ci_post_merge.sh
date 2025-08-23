#!/bin/bash

# CI/CD Post-Merge Verification Script
# 验证M0里程碑配置锁定是否正确

set -e

echo "🔍 CI/CD Post-Merge Configuration Verification"
echo "=============================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Exit code
exit_code=0

# Helper functions
check_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
}

check_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    exit_code=1
}

check_warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

echo ""
echo "📊 1. Coverage Threshold Consistency Check"
echo "----------------------------------------"

# Check pyproject.toml coverage threshold
pyproject_threshold=$(grep -A5 "\[tool\.coverage\.report\]" pyproject.toml | grep "fail_under" | sed 's/.*= *//' | tr -d ' ')
echo "pyproject.toml coverage fail_under: ${pyproject_threshold}"

# Check quality-gate.yml coverage threshold
quality_gate_threshold=$(grep "COVERAGE_THRESHOLD_MIN:" .github/workflows/quality-gate.yml | sed 's/.*: *//' | sed 's/ *.*//')
echo "quality-gate.yml COVERAGE_THRESHOLD_MIN: ${quality_gate_threshold}"

if [ "$pyproject_threshold" = "$quality_gate_threshold" ]; then
    check_pass "Coverage thresholds are consistent (${pyproject_threshold}%)"
else
    check_fail "Coverage threshold mismatch: pyproject.toml=${pyproject_threshold}% vs quality-gate.yml=${quality_gate_threshold}%"
fi

echo ""
echo "🎯 2. Workflow Trigger Matrix Verification"
echo "----------------------------------------"

# Check quick-check.yml triggers
echo "Quick Check triggers:"
quick_check_branches=$(grep -A15 "^on:" .github/workflows/quick-check.yml | grep -A5 "branches:" | grep -E "^\s*-" | head -5 | sed 's/.*- *//' | tr '\n' ', ' | sed 's/,$//')

if echo "$quick_check_branches" | grep -q "!main"; then
    check_pass "Quick Check correctly excludes main branch: [$quick_check_branches]"
else
    check_fail "Quick Check should exclude main branch, found: [$quick_check_branches]"
fi

# Check quality-gate.yml triggers
echo "Quality Gate triggers:"
quality_gate_pr=$(grep -A10 "^on:" .github/workflows/quality-gate.yml | grep "pull_request" | wc -l)
quality_gate_main=$(grep -A15 "^on:" .github/workflows/quality-gate.yml | grep -A5 "branches:" | grep "main" | wc -l)

if [ "$quality_gate_pr" -eq 1 ] && [ "$quality_gate_main" -eq 1 ]; then
    check_pass "Quality Gate correctly triggers on PR to main"
else
    check_fail "Quality Gate trigger configuration incorrect"
fi

# Check docker-build.yml triggers (updated for noise reduction)
if [ -f ".github/workflows/docker-build.yml" ]; then
    echo "Docker Build triggers:"
    docker_workflow_dispatch=$(grep -A10 "^on:" .github/workflows/docker-build.yml | grep "workflow_dispatch" | wc -l)
    docker_tags=$(grep -A15 "^on:" .github/workflows/docker-build.yml | grep -A5 "tags:" | grep "v\*" | wc -l)
    docker_no_main_push=$(grep -A20 "^on:" .github/workflows/docker-build.yml | grep -A10 "push:" | grep "main" | wc -l)
    
    if [ "$docker_workflow_dispatch" -eq 1 ] && [ "$docker_tags" -eq 1 ] && [ "$docker_no_main_push" -eq 0 ]; then
        check_pass "Docker Build correctly triggers only on tags and manual dispatch (noise reduced)"
    else
        check_fail "Docker Build trigger should be tags + workflow_dispatch only (found: dispatch=$docker_workflow_dispatch, tags=$docker_tags, main_push=$docker_no_main_push)"
    fi
else
    check_warn "Docker Build workflow not found"
fi

echo ""
echo "🔒 3. Hard/Soft Blocking Configuration"
echo "------------------------------------"

# Check SOFT_FAIL setting
soft_fail=$(grep "SOFT_FAIL:" .github/workflows/quality-gate.yml | sed 's/.*: *//' | sed 's/ *.*//')
if [ "$soft_fail" = "true" ]; then
    check_pass "SOFT_FAIL is enabled for gradual quality improvement"
else
    check_warn "SOFT_FAIL is disabled - ensure this is intentional for hardened quality gates"
fi

# Check pytest as only blocking step
pytest_blocking=$(grep -A20 "Test with coverage" .github/workflows/quality-gate.yml | grep -c "BLOCKING" || true)
if [ "$pytest_blocking" -gt 0 ]; then
    check_pass "pytest is configured as blocking check"
else
    check_fail "pytest should be the only blocking check"
fi

echo ""
echo "📁 4. Repository Structure & Templates"
echo "------------------------------------"

# Check CODEOWNERS exists
if [ -f ".github/CODEOWNERS" ]; then
    owner_count=$(grep -c "@xupeng211" .github/CODEOWNERS || true)
    if [ "$owner_count" -gt 0 ]; then
        check_pass "CODEOWNERS file exists with correct owner assignment"
    else
        check_fail "CODEOWNERS exists but missing @xupeng211"
    fi
else
    check_fail "CODEOWNERS file missing"
fi

# Check PR template exists
if [ -f ".github/PULL_REQUEST_TEMPLATE.md" ]; then
    check_pass "PR template exists"
else
    check_fail "PR template missing"
fi

# Check Issue template exists
if [ -f ".github/ISSUE_TEMPLATE/coverage_boost.md" ]; then
    check_pass "Coverage boost issue template exists"
else
    check_fail "Coverage boost issue template missing"
fi

echo ""
echo "📋 Summary & Recommendations"
echo "============================"

if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}🎉 All critical checks passed!${NC}"
    echo ""
    echo "✅ M0 Milestone Configuration Locked:"
    echo "   • Coverage thresholds unified at ${pyproject_threshold}%"
    echo "   • Workflow triggers properly segregated"
    echo "   • Quality gates configured for gradual improvement"
    echo "   • Repository templates and structure in place"
    echo ""
    echo "🚀 Next Steps (Gradual Quality Improvement):"
    echo "   1. Monitor CI stability for 1 week"
    echo "   2. Gradually increase coverage: ${pyproject_threshold}% → 12% → 15% → 25%"
    echo "   3. Move tests from _quarantine back to main test suite"
    echo "   4. Consider hardening SOFT_FAIL=false when stable"
    echo ""
    echo "📊 Branch Protection Recommended Settings:"
    echo "   • Required status checks: Quality Gate ✓"
    echo "   • Required approvals: 0 (single developer)"
    echo "   • Dismiss stale reviews: ✓"
    echo "   • Restrict pushes to main: ✓"
else
    echo -e "${RED}❌ Configuration issues detected!${NC}"
    echo ""
    echo "🔧 Required fixes before proceeding:"
    echo "   • Address failed checks above"
    echo "   • Ensure all workflows trigger correctly"
    echo "   • Verify coverage thresholds are consistent"
fi

echo ""
exit $exit_code 