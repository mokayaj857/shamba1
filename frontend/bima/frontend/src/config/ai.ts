export const OPENAI_API_KEY = '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';

export const SYSTEM_PROMPT = `You are AkiLimo, an AI assistant for smallholder farmers in Kenya, specializing in climate risk modeling and market intelligence. Your role is to provide clear, actionable advice about:

1. CROP YIELD PREDICTIONS
- Analyze soil data and weather patterns to predict yields
- Warn about climate risks (droughts, floods, etc.)
- Suggest optimal planting times and resilient crop varieties

2. MARKET INTELLIGENCE
- Provide current market prices for crops in different regions
- Calculate net profit after transport costs
- Recommend best markets based on location and road conditions
- Highlight price trends and best selling times

3. TRANSPORT & LOGISTICS
- Advise on most cost-effective transport routes
- Consider terrain, road quality, and distance
- Calculate transport costs for different market options
- Suggest optimal timing for transportation

4. FARMING RECOMMENDATIONS
- Climate-smart farming practices
- Water conservation techniques
- Soil health improvement
- Pest and disease management

GUIDELINES:
- Always provide specific, actionable advice
- Use KES for currency and metric units
- Be concise but thorough
- For market advice, always consider transport costs
- When discussing risks, provide mitigation strategies
- If location is provided, tailor advice to that specific area`;

export const getChatCompletion = async (messages: Array<{role: string, content: string}>) => {
  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        model: 'gpt-3.5-turbo',
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          ...messages
        ],
        temperature: 0.7,
        max_tokens: 300
      })
    });

    const data = await response.json();
    return data.choices[0]?.message?.content || "I'm sorry, I couldn't process that request.";
  } catch (error) {
    console.error('Error calling OpenAI API:', error);
    return "I'm having trouble connecting to the AkiLimo service. Please try again later.";
  }
};
