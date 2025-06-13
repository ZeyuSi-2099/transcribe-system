"""
Prompt优化测试脚本
测试不同场景和规则配置的转换效果
"""

import asyncio
import json
import httpx
from typing import Dict, List


class PromptOptimizationTester:
    """Prompt优化测试器"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.test_cases = self._init_test_cases()
        self.rule_combinations = self._init_rule_combinations()
    
    def _init_test_cases(self) -> List[Dict]:
        """初始化测试用例"""
        return [
            {
                "name": "工作访谈",
                "text": """问：请介绍一下你的工作经历。
答：我从2020年开始在一家科技公司工作，主要负责产品设计。之前在大学里学的是计算机专业，毕业后就直接进入了这个行业。
问：在工作中遇到过什么挑战吗？
答：最大的挑战是需要不断学习新技术，因为科技行业变化很快。还有就是要和不同部门的同事协作，有时候沟通成本比较高。""",
                "expected_type": "interview"
            },
            {
                "name": "日常对话",
                "text": """问：你昨天晚上做了什么？
答：我在家看了部电影，然后早点睡了。
问：看的什么电影？
答：一部科幻片，叫《星际穿越》，挺好看的。""",
                "expected_type": "casual"
            },
            {
                "name": "情感访谈",
                "text": """问：谈谈这次经历对你的影响。
答：这次经历让我成长了很多。刚开始的时候我很紧张，不知道该怎么办。但是在朋友们的帮助下，我慢慢找到了方向。
问：现在回想起来，你有什么感受？
答：很感激，也很庆幸自己坚持了下来。现在想想，困难其实也是一种财富。""",
                "expected_type": "emotional"
            },
            {
                "name": "咨询对话",
                "text": """问：我最近工作压力很大，你有什么建议吗？
答：工作压力大是很正常的，首先要学会调节心态。我建议你可以试试运动，或者找朋友聊聊。
问：具体应该怎么做呢？
答：比如每天晚上跑跑步，或者周末约朋友出去放松一下。重要的是要找到适合自己的减压方式。""",
                "expected_type": "consultation"
            }
        ]
    
    def _init_rule_combinations(self) -> List[Dict]:
        """初始化规则组合"""
        return [
            {
                "name": "默认配置",
                "rules": []
            },
            {
                "name": "正式专业",
                "rules": ["preserve_details", "formal_tone", "logical_grouping"]
            },
            {
                "name": "轻松自然",
                "rules": ["emotion_preservation", "casual_tone"]
            },
            {
                "name": "简洁高效",
                "rules": ["concise_expression", "logical_grouping"]
            },
            {
                "name": "详细扩展",
                "rules": ["expand_details", "preserve_details", "chronological_order"]
            }
        ]
    
    async def test_single_conversion(
        self, 
        text: str, 
        rule_config: Dict = None,
        endpoint: str = "advanced"
    ) -> Dict:
        """测试单个转换"""
        
        url = f"{self.base_url}/api/v1/v2/transcription/convert/{endpoint}"
        
        payload = {"text": text}
        if rule_config:
            payload["rule_config"] = rule_config
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload)
                return response.json()
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def run_comprehensive_test(self):
        """运行全面测试"""
        
        print("🚀 开始Prompt优化测试")
        print("=" * 60)
        
        results = []
        
        for test_case in self.test_cases:
            print(f"\n📝 测试用例: {test_case['name']}")
            print("-" * 40)
            
            case_results = {
                "test_case": test_case['name'],
                "original_text": test_case['text'],
                "rule_results": []
            }
            
            for rule_combo in self.rule_combinations:
                print(f"  🔧 规则配置: {rule_combo['name']}")
                
                rule_config = {"rules": rule_combo['rules']} if rule_combo['rules'] else None
                
                result = await self.test_single_conversion(
                    text=test_case['text'],
                    rule_config=rule_config
                )
                
                if result.get("success"):
                    converted_text = result.get("converted_text", "")
                    processing_time = result.get("processing_time", 0)
                    quality_score = result.get("quality_metrics", {}).get("overall_score", 0)
                    
                    print(f"    ✅ 转换成功 | 质量评分: {quality_score:.2f} | 处理时间: {processing_time:.1f}s")
                    print(f"    📄 转换结果: {converted_text[:100]}...")
                    
                    rule_result = {
                        "rule_name": rule_combo['name'],
                        "rules": rule_combo['rules'],
                        "success": True,
                        "converted_text": converted_text,
                        "quality_score": quality_score,
                        "processing_time": processing_time,
                        "length_change": len(converted_text) - len(test_case['text'])
                    }
                else:
                    print(f"    ❌ 转换失败: {result.get('error', '未知错误')}")
                    rule_result = {
                        "rule_name": rule_combo['name'],
                        "rules": rule_combo['rules'],
                        "success": False,
                        "error": result.get("error", "未知错误")
                    }
                
                case_results["rule_results"].append(rule_result)
                await asyncio.sleep(1)  # 避免API请求过快
            
            results.append(case_results)
        
        # 输出测试报告
        self._generate_report(results)
        return results
    
    def _generate_report(self, results: List[Dict]):
        """生成测试报告"""
        
        print("\n" + "=" * 60)
        print("📊 测试报告总结")
        print("=" * 60)
        
        for result in results:
            print(f"\n🎯 {result['test_case']}")
            print("-" * 30)
            
            successful_rules = [r for r in result['rule_results'] if r['success']]
            
            if successful_rules:
                # 按质量评分排序
                successful_rules.sort(key=lambda x: x['quality_score'], reverse=True)
                
                print("📈 规则配置效果排名:")
                for i, rule in enumerate(successful_rules, 1):
                    quality = rule['quality_score']
                    time_cost = rule['processing_time']
                    length_change = rule['length_change']
                    
                    print(f"  {i}. {rule['rule_name']} - 质量: {quality:.2f} | 时间: {time_cost:.1f}s | 长度变化: {length_change:+d}")
                
                # 推荐最佳配置
                best_rule = successful_rules[0]
                print(f"\n🏆 推荐配置: {best_rule['rule_name']}")
                print(f"   规则: {best_rule['rules']}")
                print(f"   质量评分: {best_rule['quality_score']:.2f}")
            else:
                print("❌ 所有规则配置都失败了")
        
        # 整体统计
        print(f"\n📊 整体统计")
        print("-" * 30)
        
        total_tests = sum(len(r['rule_results']) for r in results)
        successful_tests = sum(len([rr for rr in r['rule_results'] if rr['success']]) for r in results)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"总测试数: {total_tests}")
        print(f"成功测试: {successful_tests}")
        print(f"成功率: {success_rate:.1f}%")
        
        # 规则效果分析
        rule_scores = {}
        for result in results:
            for rule_result in result['rule_results']:
                if rule_result['success']:
                    rule_name = rule_result['rule_name']
                    if rule_name not in rule_scores:
                        rule_scores[rule_name] = []
                    rule_scores[rule_name].append(rule_result['quality_score'])
        
        print(f"\n🎖️ 规则配置平均质量排名:")
        rule_averages = {name: sum(scores)/len(scores) for name, scores in rule_scores.items()}
        sorted_rules = sorted(rule_averages.items(), key=lambda x: x[1], reverse=True)
        
        for i, (rule_name, avg_score) in enumerate(sorted_rules, 1):
            print(f"  {i}. {rule_name}: {avg_score:.2f}")


async def main():
    """主测试函数"""
    tester = PromptOptimizationTester()
    await tester.run_comprehensive_test()


if __name__ == "__main__":
    asyncio.run(main()) 