# Day 1: AI Systems and How LLMs Work

## What are Artificial Intelligence Systems?

Artificial intelligence (AI) systems are software or hardware setups designed to mimic or surpass human cognitive functions. They process data to perceive their environment, reason through information, learn from experience, and take action to achieve a specific goal.

## Core Components of AI Systems

An AI system can be understood as four phases in a cycle:

1. **Data input:** the system gathers data from sources such as sensors, websites and databases.
2. **Processing and reasoning:** algorithms such as machine learning and neural networks analyse the data to find underlying patterns.
3. **Decision making:** the system predicts an outcome, answers a query, or performs an action based on its analysis.
4. **Learning (feedback loop):** the system evaluates how well its output worked and refines its mathematical rules to improve future accuracy.

## Types of AI Systems

AI systems are classified by their capability and by how they process information.

### 1. Classification by Capability

This measures the power and scope of an AI system against human intelligence.

- **Artificial Narrow Intelligence (ANI / Weak AI):** the only type that exists today. These systems are specialised for a single task, such as playing chess, translating text or generating language like an LLM. They cannot apply their skills outside that task.
- **Artificial General Intelligence (AGI / Strong AI):** a theoretical AI with human-level cognitive ability. An AGI could learn, understand, reason and adapt to any intellectual task a human can.
- **Artificial Superintelligence (ASI):** a hypothetical future AI that far surpasses human intelligence in every field, including creativity, general wisdom and social skills.

### 2. Classification by Functionality

This scale categorises AI by how it interacts with the world and whether it can remember past events.

- **Reactive machines:** the most basic AI. They store no memories and use no past experience. They look at a live situation and respond with predefined logic.
  *Examples:* IBM's Deep Blue chess computer, basic email spam filters.
- **Limited memory AI:** stores past data for a short period to make better decisions. Most modern machine learning applications fall here.
  *Examples:* self-driving cars (which track the speed and direction of other cars over time) and LLMs (which use the context of your chat history).
- **Theory of mind AI:** an advanced, experimental stage. These systems would understand human emotions, beliefs and thoughts and adjust their behaviour to the user's psychological state.
- **Self-aware AI:** a purely theoretical extension of theory of mind. These systems would have their own consciousness, self-awareness and desires, essentially becoming sentient.

---

## What are LLMs?

Large language models (LLMs) are AI systems trained on massive amounts of text to understand, summarise, translate and generate human-like language. Common examples are ChatGPT (OpenAI), Claude (Anthropic) and Gemini (Google).

## How LLMs work: tokens, next-token prediction, context windows

- Most LLMs use a deep learning architecture called a **transformer**, which relies on a **self-attention** mechanism to process words in relation to one another across entire sentences.
- At their core, LLMs perform a statistical task: they predict the next piece of text, called a **token** (a whole word or part of a word), based on the input they receive.
- Models are first **pretrained** on large datasets using self-supervised learning, then refined with techniques such as **reinforcement learning from human feedback (RLHF)** so they follow instructions safely.
- In short, LLMs are very advanced pattern-matching engines that calculate probabilities, built on three concepts: tokens, next-token prediction and context windows.

### 1. Tokens

LLMs don't read text as strings of letters. Text is broken into smaller pieces called tokens, and each token is mapped to a unique numerical ID. This lets the model handle vast amounts of data and find mathematical relationships between pieces of text.

### 2. Next-token prediction

An LLM does one mathematical task over and over: it looks at a sequence of tokens and predicts the most likely next token.

- **Probability maps:** given "The cat sat on the", the model assigns a probability to thousands of possible next tokens. For example, *mat* might get 60%, *floor* 25% and *moon* 0.001% (illustrative numbers).
- **Self-attention:** the transformer looks at all the tokens in the prompt at once and weighs which are most important. In "The bank of the river was muddy", attention links "bank" to "river", so the model reads it as land, not a financial building.
- **Temperature:** if the model always picked the highest-probability token, its output would be rigid and repetitive. A setting called temperature lets it sometimes pick the 2nd or 3rd most likely token, which makes output more varied and human-like.

### 3. Context windows

The context window is the model's total capacity, or "memory limit", in a single conversation. It sets how much text the model can look at when predicting the next token.

- **In and out:** the window includes both your prompt and the text the model generates.
- **The invisible limit:** a model with an 8,000-token window can hold only about 6,000 English words at a time.
- **When it fills up:** once a conversation exceeds the window, the oldest tokens are dropped to make room for new ones, so the model can no longer use what you said earlier.
- **Note:** newer models have much larger windows, from 128,000 to over 1 million tokens, which can hold entire books or codebases in one session.

---

## Self-check

**Why can the same text cost a different number of tokens on two models?**
Each model uses its own tokenizer, which splits text into different subword pieces. So the token count differs, and since providers bill per token, so does the cost.