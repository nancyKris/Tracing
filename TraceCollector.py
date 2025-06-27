import requests
import csv
from typing import List, Dict

class TraceCollector:
    def __init__(self, agent_endpoints: Dict[str, str]):
        """
        :param agent_endpoints: Dict mapping agent identifiers to their log endpoint URLs
        """
        self.agent_endpoints = agent_endpoints

    def collect_logs(self) -> List[Dict]:
        """
        Collect logs from all agents.
        :return: List of log entries, each as a dict with agent_id, timestamp, and message.
        """
        all_logs = []
        for agent_id, endpoint in self.agent_endpoints.items():
            try:
                response = requests.get(endpoint)
                response.raise_for_status()
                logs = response.json()  # Expecting a list of dicts with 'timestamp' and 'message'
                for log in logs:
                    all_logs.append({
                        'agent_id': agent_id,
                        'timestamp': log.get('timestamp', ''),
                        'message': log.get('message', '')
                    })
            except Exception as e:
                print(f"Failed to collect logs from {agent_id} at {endpoint}: {e}")
        return all_logs

    def save_to_csv(self, logs: List[Dict], filename: str):
        """
        Save collected logs to a CSV file.
        :param logs: List of log entries.
        :param filename: Output CSV file name.
        """
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['agent_id', 'timestamp', 'message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for log in logs:
                writer.writerow(log)

class FailureAnalyzer:
    def __init__(self, logs: List[Dict]):
        """
        :param logs: List of log entries (dicts with 'agent_id', 'timestamp', 'message')
        """
        self.logs = logs
        self.agent_failures = self._group_failures_by_agent()

    def _categorize_failure(self, msg: str) -> str:
        msg_lower = msg.lower()
        if any(kw in msg_lower for kw in ['syntax error', 'compile error', 'compilation failed', 'unexpected indent', 'invalid syntax']):
            return 'Syntax / compile error'
        elif any(kw in msg_lower for kw in ['assertion failed', 'test failed', 'logic error', 'incorrect result', 'wrong output', 'failed test', 'did not pass', 'mismatch']):
            return 'Logic / test failure'
        elif 'timeout' in msg_lower or 'timed out' in msg_lower:
            return 'Timeout'
        elif any(kw in msg_lower for kw in ['hallucination', 'nonsensical', 'made up', 'fabricated', 'not in context', 'irrelevant', 'llm error', 'llm mistake']):
            return 'LLM hallucination'
        else:
            return 'Other'

    def _group_failures_by_agent(self) -> Dict[str, List[Dict]]:
        failures = {}
        for log in self.logs:
            agent_id = log.get('agent_id', 'unknown')
            msg = log.get('message', '')
            # Simple heuristic: classify as failure if 'fail' or 'error' in message (case-insensitive)
            if any(word in msg.lower() for word in ['fail', 'error', 'exception', 'crash', 'timeout', 'hallucination']):
                if agent_id not in failures:
                    failures[agent_id] = []
                categorized = self._categorize_failure(msg)
                failures[agent_id].append({
                    **log,
                    'category': categorized
                })
        return failures

    def classify_failures(self) -> Dict[str, List[Dict]]:
        """
        Returns a dict mapping agent_id to a list of classified failure logs (with categories).
        """
        return self.agent_failures

class FailurePropagationMonitor:
    def __init__(self, logs: List[Dict]):
        """
        :param logs: List of log entries (dicts with 'agent_id', 'timestamp', 'message')
        """
        self.logs = sorted(logs, key=lambda x: x.get('timestamp', ''))

    def map_failure_propagation(self) -> List[Dict]:
        """
        Attempts to map how failures propagate across agents by analyzing the sequence of failure logs.
        Returns a list of propagation steps, each as a dict with source_agent, target_agent, timestamp, and message.
        """
        propagation = []
        last_failure = None
        for log in self.logs:
            msg = log.get('message', '').lower()
            if any(word in msg for word in ['fail', 'error', 'exception', 'crash']):
                if last_failure:
                    # If the current failure is from a different agent, consider it propagated
                    if log['agent_id'] != last_failure['agent_id']:
                        propagation.append({
                            'source_agent': last_failure['agent_id'],
                            'target_agent': log['agent_id'],
                            'timestamp': log['timestamp'],
                            'message': log['message']
                        })
                last_failure = log
        return propagation

    def show_propagation(self):
        propagation = self.map_failure_propagation()
        if not propagation:
            print("No failure propagation detected across agents.")
            return
        print("Failure Propagation Map:")
        for step in propagation:
            print(f"  {step['source_agent']} -> {step['target_agent']} at {step['timestamp']}: {step['message']}")

    def show_failure_introducers(self):
        """
        Prints which agent introduced each unique failure message/type.
        """
        seen = {}
        for log in self.logs:
            msg = log.get('message', '').strip()
            if any(word in msg.lower() for word in ['fail', 'error', 'exception', 'crash', 'timeout', 'hallucination']):
                if msg not in seen:
                    seen[msg] = log['agent_id']
        print("\nFailure Introduction Map:")
        for msg, agent in seen.items():
            print(f"  Failure: '{msg}' introduced by agent: {agent}")

    @staticmethod
    def patch_propagation_analysis(logs_before: List[Dict], logs_after: List[Dict]) -> Dict[str, Dict]:
        """
        Compares logs before and after a patch to determine:
        - If a patch partially fixed a failure (reduced but not eliminated)
        - If a patch introduced a new failure (new message/type appears after patch)
        Returns a dict per agent with details.
        """
        from collections import defaultdict
        def extract_failures(logs):
            failures = defaultdict(list)
            for log in logs:
                agent_id = log.get('agent_id', 'unknown')
                msg = log.get('message', '').strip()
                if any(word in msg.lower() for word in ['fail', 'error', 'exception', 'crash', 'timeout', 'hallucination']):
                    failures[agent_id].append(msg)
            return failures
        before = extract_failures(logs_before)
        after = extract_failures(logs_after)
        all_agents = set(before.keys()) | set(after.keys())
        result = {}
        for agent in all_agents:
            before_set = set(before.get(agent, []))
            after_set = set(after.get(agent, []))
            fixed = before_set - after_set
            partial = before_set & after_set
            introduced = after_set - before_set
            result[agent] = {
                'fully_fixed': list(fixed),
                'partially_fixed': list(partial),
                'newly_introduced': list(introduced)
            }
        return result

class PatchEvaluator:
    def __init__(self, logs_before: List[Dict], logs_after: List[Dict]):
        """
        :param logs_before: List of log entries before patch (dicts with 'agent_id', 'timestamp', 'message')
        :param logs_after: List of log entries after patch
        """
        self.logs_before = logs_before
        self.logs_after = logs_after

    def evaluate_patch_effectiveness(self) -> Dict[str, str]:
        """
        Evaluates patch effectiveness per agent by comparing failure counts before and after.
        Returns a dict mapping agent_id to an evaluation string.
        """
        def count_failures(logs):
            failures = {}
            for log in logs:
                agent_id = log.get('agent_id', 'unknown')
                if any(word in log.get('message', '').lower() for word in ['fail', 'error', 'exception', 'crash']):
                    failures[agent_id] = failures.get(agent_id, 0) + 1
            return failures

        before = count_failures(self.logs_before)
        after = count_failures(self.logs_after)
        all_agents = set(before.keys()) | set(after.keys())
        evaluation = {}
        for agent in all_agents:
            b = before.get(agent, 0)
            a = after.get(agent, 0)
            if b == 0 and a == 0:
                evaluation[agent] = 'No failures before or after patch.'
            elif b > 0 and a == 0:
                evaluation[agent] = f'All failures resolved (before: {b}, after: 0).'
            elif b == 0 and a > 0:
                evaluation[agent] = f'New failures introduced (before: 0, after: {a}).'
            elif a < b:
                evaluation[agent] = f'Failures reduced (before: {b}, after: {a}).'
            elif a == b:
                evaluation[agent] = f'No change in failures (before: {b}, after: {a}).'
            else:
                evaluation[agent] = f'Failures increased (before: {b}, after: {a}).'
        return evaluation

    def advanced_evaluation_report(self) -> Dict[str, Dict]:
        """
        Provides an advanced evaluation per agent:
        - Failure type breakdown before/after
        - Time to recovery (if any)
        - Diversity of failure messages before/after
        Returns a dict mapping agent_id to a report dict.
        """
        from collections import defaultdict
        from datetime import datetime

        def classify_failure_type(msg):
            msg = msg.lower()
            if 'timeout' in msg:
                return 'timeout'
            elif 'connection' in msg:
                return 'connection'
            elif 'resource' in msg:
                return 'resource'
            elif 'memory' in msg:
                return 'memory'
            elif 'disk' in msg:
                return 'disk'
            elif 'exception' in msg:
                return 'exception'
            elif 'crash' in msg:
                return 'crash'
            elif 'fail' in msg:
                return 'fail'
            elif 'error' in msg:
                return 'error'
            else:
                return 'other'

        def parse_time(ts):
            try:
                return datetime.fromisoformat(ts)
            except Exception:
                return None

        # Group logs by agent
        def group_by_agent(logs):
            grouped = defaultdict(list)
            for log in logs:
                grouped[log.get('agent_id', 'unknown')].append(log)
            return grouped

        before_grouped = group_by_agent(self.logs_before)
        after_grouped = group_by_agent(self.logs_after)
        all_agents = set(before_grouped.keys()) | set(after_grouped.keys())
        report = {}
        for agent in all_agents:
            before_logs = before_grouped.get(agent, [])
            after_logs = after_grouped.get(agent, [])
            # Failure type breakdown
            before_types = defaultdict(int)
            after_types = defaultdict(int)
            before_msgs = set()
            after_msgs = set()
            last_failure_time = None
            first_success_time = None
            for log in before_logs:
                msg = log.get('message', '')
                if any(word in msg.lower() for word in ['fail', 'error', 'exception', 'crash']):
                    ftype = classify_failure_type(msg)
                    before_types[ftype] += 1
                    before_msgs.add(msg)
                    t = parse_time(log.get('timestamp', ''))
                    if t and (last_failure_time is None or t > last_failure_time):
                        last_failure_time = t
            for log in after_logs:
                msg = log.get('message', '')
                if any(word in msg.lower() for word in ['fail', 'error', 'exception', 'crash']):
                    ftype = classify_failure_type(msg)
                    after_types[ftype] += 1
                    after_msgs.add(msg)
                else:
                    # Consider as success if not a failure message
                    t = parse_time(log.get('timestamp', ''))
                    if t and last_failure_time and (first_success_time is None or t < first_success_time) and t > last_failure_time:
                        first_success_time = t
            # Time to recovery
            time_to_recovery = None
            if last_failure_time and first_success_time:
                delta = first_success_time - last_failure_time
                time_to_recovery = str(delta)
            report[agent] = {
                'failure_types_before': dict(before_types),
                'failure_types_after': dict(after_types),
                'unique_failure_messages_before': len(before_msgs),
                'unique_failure_messages_after': len(after_msgs),
                'time_to_recovery': time_to_recovery,
            }
        return report

# Example usage:
if __name__ == "__main__":
    agent_endpoints = {
        'agent1': 'http://localhost:5001/logs',
        'agent2': 'http://localhost:5002/logs',
    }
    collector = TraceCollector(agent_endpoints)
    logs = collector.collect_logs()
    collector.save_to_csv(logs, 'mas_logs.csv')

    # Analyze failures per agent
    analyzer = FailureAnalyzer(logs)
    failures_by_agent = analyzer.classify_failures()
    for agent_id, failures in failures_by_agent.items():
        print(f"Failures for {agent_id}:")
        for failure in failures:
            print(f"  [{failure['timestamp']}] {failure['message']} (Category: {failure['category']})")

    # Monitor and show failure propagation
    propagation_monitor = FailurePropagationMonitor(logs)
    propagation_monitor.show_propagation()
    propagation_monitor.show_failure_introducers()

    # Example PatchEvaluator usage (replace with real logs before/after patch)
    logs_before_patch = logs  # In practice, load or collect logs before patch
    logs_after_patch = logs   # In practice, load or collect logs after patch
    patch_evaluator = PatchEvaluator(logs_before_patch, logs_after_patch)
    patch_results = patch_evaluator.evaluate_patch_effectiveness()
    print("\nPatch Effectiveness Evaluation:")
    for agent, result in patch_results.items():
        print(f"  {agent}: {result}")

    # Advanced patch evaluation
    print("\nAdvanced Patch Evaluation Report:")
    advanced_report = patch_evaluator.advanced_evaluation_report()
    for agent, details in advanced_report.items():
        print(f"Agent: {agent}")
        print(f"  Failure types before: {details['failure_types_before']}")
        print(f"  Failure types after: {details['failure_types_after']}")
        print(f"  Unique failure messages before: {details['unique_failure_messages_before']}")
        print(f"  Unique failure messages after: {details['unique_failure_messages_after']}")
        print(f"  Time to recovery: {details['time_to_recovery']}")

    # Patch propagation analysis
    patch_propagation = FailurePropagationMonitor.patch_propagation_analysis(logs_before_patch, logs_after_patch)
    print("\nPatch Propagation Analysis:")
    for agent, details in patch_propagation.items():
        print(f"Agent: {agent}")
        print(f"  Fully fixed failures: {details['fully_fixed']}")
        print(f"  Partially fixed (still present) failures: {details['partially_fixed']}")
        print(f"  Newly introduced failures: {details['newly_introduced']}") 