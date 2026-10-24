from typing import Callable

from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain


def run_reserach_pipeline(
    topic: str,
    progress_callback: Callable[[str, str], None] | None = None,
) -> dict:
    state = {}

    def report_progress(stage: str, status: str) -> None:
        if progress_callback is not None:
            progress_callback(stage, status)

    # Search for the topic.
    report_progress("search", "running")
    print("\n"+" ="*50)
    print("Step 1. Search Agent is working....")
    print("="*50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}") ]
    })

    state["search_results"] = search_result["messages"][-1].content
    print("\nSearch results:\n", state["search_results"])
    report_progress("search", "complete")


    # Research the most relevant search result.
    report_progress("read", "running")
    print("\n"+" ="*50)
    print("Step 2. Reader Agent is scraping the content....")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}',"
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800] }"
        )]
    })

    state['scraped_content'] = reader_result['messages'][-1].content
    print("\nscraped content: \n", state['scraped_content'])
    report_progress("read", "complete")


    # Draft the report.
    report_progress("write", "running")
    print("\n"+" ="*50)
    print("Step 3. Writer is drafting the report....")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content' ]}"
    )
    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })

    print("\n Final Report\n", state['report'])
    report_progress("write", "complete")


    # Review the report.
    report_progress("review", "running")
    print("\n"+" ="*50)
    print("Step 4. Critic is reviwing the report....")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "report" : state['report' ]
    })

    print("\n critic report \n", state['feedback' ])
    report_progress("review", "complete")

    return state


if __name__ == "__main__":
    topic = input("Enter your research topic:  ")
    run_reserach_pipeline(topic)