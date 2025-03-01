"""
Utility functions for trace processing.
"""
from typing import Dict, Any

def process_trace_data(trace_data: Dict[str, Any], agent_traces: bool, trace_level: str) -> None:
    """
    Process and display trace information from the agent
    
    Args:
        trace_data: The trace data from the agent response
        agent_traces: Whether agent traces are enabled
        trace_level: The trace level (none, minimal, standard, detailed)
    """
    # Skip trace processing if agent_traces is disabled or trace level is none
    if not agent_traces or trace_level == "none":
        return
        
    if not trace_data or not isinstance(trace_data, dict) or "trace" not in trace_data:
        return
        
    trace = trace_data["trace"]
    
    # Process orchestration trace (main reasoning and decision making)
    if "orchestrationTrace" in trace:
        orchestration = trace["orchestrationTrace"]
        
        # Display model reasoning if available (all trace levels)
        if "modelInvocationOutput" in orchestration and "reasoningContent" in orchestration["modelInvocationOutput"]:
            reasoning = orchestration["modelInvocationOutput"]["reasoningContent"]
            if "reasoningText" in reasoning and "text" in reasoning["reasoningText"]:
                reasoning_text = reasoning["reasoningText"]["text"]
                print("\n" + "=" * 80)
                print("[AGENT TRACE] Reasoning Process:")
                print("-" * 80)
                print(reasoning_text)
                print("=" * 80)
        
        # Display rationale if available (all trace levels)
        if "rationale" in orchestration and "text" in orchestration["rationale"]:
            rationale_text = orchestration["rationale"]["text"]
            print("\n" + "=" * 80)
            print("[AGENT TRACE] Decision Rationale:")
            print("-" * 80)
            print(rationale_text)
            print("=" * 80)
            
        # Display invocation input if available (standard and detailed levels)
        if trace_level in ["standard", "detailed"] and "invocationInput" in orchestration:
            invocation = orchestration["invocationInput"]
            invocation_type = invocation.get("invocationType", "Unknown")
            
            print("\n" + "-" * 80)
            print(f"[AGENT TRACE] Invocation Type: {invocation_type}")
            
            # Show action group invocation details
            if "actionGroupInvocationInput" in invocation:
                action_input = invocation["actionGroupInvocationInput"]
                action_group = action_input.get("actionGroupName", "Unknown")
                function = action_input.get("function", "Unknown")
                parameters = action_input.get("parameters", [])
                
                print(f"[AGENT TRACE] Action Group: {action_group}")
                print(f"[AGENT TRACE] Function: {function}")
                if parameters:
                    print("[AGENT TRACE] Parameters:")
                    for param in parameters:
                        print(f"  - {param.get('name')}: {param.get('value')} ({param.get('type', 'unknown')})")
            print("-" * 80)
    
    # Only process these traces for detailed level
    if trace_level == "detailed":
        # Process pre-processing trace
        if "preProcessingTrace" in trace and "modelInvocationOutput" in trace["preProcessingTrace"]:
            pre_processing = trace["preProcessingTrace"]["modelInvocationOutput"]
            if "parsedResponse" in pre_processing:
                parsed = pre_processing["parsedResponse"]
                if "rationale" in parsed:
                    print("\n" + "-" * 80)
                    print("[AGENT TRACE] Pre-processing Rationale:")
                    print(parsed["rationale"])
                    print("-" * 80)
        
        # Process post-processing trace
        if "postProcessingTrace" in trace and "modelInvocationOutput" in trace["postProcessingTrace"]:
            post_processing = trace["postProcessingTrace"]["modelInvocationOutput"]
            if "reasoningContent" in post_processing and "reasoningText" in post_processing["reasoningContent"]:
                reasoning = post_processing["reasoningContent"]["reasoningText"]
                if "text" in reasoning:
                    print("\n" + "-" * 80)
                    print("[AGENT TRACE] Post-processing Reasoning:")
                    print(reasoning["text"])
                    print("-" * 80) 