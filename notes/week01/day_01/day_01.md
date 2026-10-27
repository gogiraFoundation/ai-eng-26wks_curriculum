What are Artificial Intelligence Systems?
     Artificial inteligence systems are computure software or hardware setup that is designed to mimic or surpase human cognitive functions.

     It processes data to perceive its environment, reaso  through information, lear  from expereince, and take action to achieve a specific goal or objective.  

Core Components of AI Syetms:
    AI systems can be divided into four broad phases or cycle 
    for easy understanding.
    
    1. Data Input: Sytem gathers data from a variety of sources such as: 
       Sensors, Websites, Databases etc

    2. Processing & Reasoning:  Advanced Algos such as ML or Neural     
        Networks analze the data to find underlying patterns.

    3. Decision Making: The system predicts an outcome, answers a query or
       performs specific actions based on its analysis.

    4. Learning (FeedBack Loop): The system evaluates the success of its   
       output and refines its mathematical rules to improve future accuracy.

Types of AI systems:
      AI systems are calssified based on their capabilities and by the way they process infomation.

      1. Classification by Functionality

      This measures the power and scope of AI systems against human intelligence. 
            
            Artificial Narrow Intelligence (ANI / Weak AI): This is the only type of AI that actually exists today. These systems are highly specialized to perform a single, specific task (like playing chess, translating text, or generating language like an LLM). They cannot apply their skills to anything outside their specific programming.

            Artificial General Intelligence (AGI / Strong AI): A theoretical type of AI that possesses human-level cognitive abilities. An AGI system could learn, understand, reason, and adapt to any intellectual task a human can

            Artificial Superintelligence (ASI): A hypothetical future AI that far surpasses human intelligence across every field, including creativity, general wisdom, and social skills
            
    2. Classification by Functionality
    
    This scale categorises AI based on how it interacts with the world and whether it can remember past events.
    
        Reactive Machines: The most basic AI systems. They do not store memories or use past experiences to make decisions. They simply look at a live situation and respond with predefined logic.   
        
        Example: IBM’s Deep Blue chess computer or basic email spam filters

        Limited Memory AI: These systems can store past data and information for a short period to make better decisions. Most modern machine learning applications fall here.
        
        Example: Self-driving cars (which track the speed/direction of other cars over time) and LLMs (which remember the context of your chat history).

        Theory of Mind AI: A highly advanced, experimental stage of AI. These systems would be able to understand human emotions, beliefs, and thoughts, adjusting their behaviour based on the psychological state of the user.


        Self-Aware AI: A purely theoretical extension of Theory of Mind. These systems would possess their own consciousness, self-awareness, and desires—essentially becoming sentient.


What are LLMs? 
    
    These are artificial intelligence systems that are trained on massive amount of text to understand, summarize, translate and generate human-like language. 

    How LLMs work: tokens, next-token prediction, context windows??
    
        Most LLMs use a deep learning framework called a transformer, which relies on a "self-attention" mechanisim to process words in relation to one another across entire sentences.
        

        At their core, LLMs perform complex statistical task, by predicting the next piece of text called a token ( tokens can be  whole word or part of a word) based on the input they receive.

        models are first pretrained on large digital datasets using sef-supervised learning, then refined through techniques like reinforcement learning from human feedback to follow instructions safely. 


        common examples are CHATGPT BY OPENAI, CLAUDE BY ANTHROPIC, GEMINI ETC

        LLMs at the core of it, are highly advance patten-matching engines that calculate probablities based on three fundamental concepts; tokens, next-token prediction, and context windows.


        1. What are Tokens??

            LLMs do not read words as strings of text, instead they are broken down into smaller pieces called tokens. Every token is
            mapped to a unique numerical id, which in turn allows the models to compress vast amount of data and easily find mathematical relationships between words.
            
        
        
        2. Next-Token Prediction
        
            At its absolute core, an LLM only does one mathematical task over and over: it looks at a sequence of tokens and predicts the most likely next token.

            Probability Maps: If you type "The cat sat on the", the model calculates a mathematical probability for thousands of possible next tokens. mat might have a 60% probability, floor might have a 25% probability, and moon might have a 0.001% probability.

            The "Self-Attention" Mechanism: The model uses the Transformer architecture to look at all the words in your prompt simultaneously. It weighs which words are most important to the context. In the sentence "The bank of the river was muddy," the attention mechanism links "bank" to "river" so it knows you mean a piece of land, not a financial building.

            Creativity (Temperature): If the model always picked the token with the highest probability, its responses would be completely rigid and repetitive. LLMs use a setting called "temperature" to occasionally pick the 2nd or 3rd most likely token, making the output feel more creative and human-like.
            
        
        3. Context Windows

                The context window is the total capacity or "memory limit" of the AI during a single conversation. It dictates how much text the model can look at when predicting the next token.

                In and Out: The context window includes both the text you type in (your prompt) and the text the AI generates back to you.

                The Invisible Limit: If a model has a context window of 8,000 tokens, it can only hold about 6,000 words in its short-term memory at one time.
                
                What Happens When It Fills Up? Once a conversation exceeds the context window, the model experiences "forgetting." It drops the oldest tokens from the beginning of the chat to make room for new ones. If you ask a question about something you said 20 pages ago, it will no longer have access to that information.

                (Note: Newer models have massive context windows—ranging from 128,000 to over 1 million tokens—allowing them to remember entire books or codebases in a single session.)























