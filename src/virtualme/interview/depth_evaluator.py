from anthropic import AsyncAnthropic

from virtualme.storage.db import Layer

DEPTH_MODEL = "claude-haiku-4-5"


async def evaluate_depth(answer: str, current_question: str, claude: AsyncAnthropic) -> Layer:
    prompt = f"""
Classify the interview answer depth as exactly one word: fact, pattern, or principle.

Question: {current_question}
Answer: {answer}
"""
    response = await claude.messages.create(
        model=DEPTH_MODEL,
        max_tokens=10,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip().lower()
    return Layer(text if text in {layer.value for layer in Layer} else Layer.FACT)
