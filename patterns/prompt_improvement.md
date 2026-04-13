# Pattern: Prompt Improvement

**Tags:** `development`, `automation`, `analysis`

## Purpose

The `prompt_improvement` pattern takes a user's initial problem statement or rough prompt and transforms it into a well-defined, optimized prompt. It applies prompt engineering best practices to ensure clarity, specificity, and effectiveness. The output is a refined prompt that will generate better results from AI models.

## Functionality

* Accept a user's problem statement, question, or initial prompt as input
* Analyze the intent and desired outcome
* Apply prompt engineering principles: clarity, specificity, context, constraints, output format
* Add relevant examples if beneficial
* Include appropriate role-setting or persona instructions
* Specify desired output format and structure
* Add constraints or guidelines to prevent common issues
* Optimize for the target use case (creative, analytical, technical, etc.)
* Return a well-structured, improved prompt ready for use

## Pattern Inputs

```yaml
inputs:
  - name: initial_prompt
    description: The user's initial problem statement, question, or rough prompt
    type: text
    required: true
    example: "Help me write a marketing email"

  - name: context
    description: Additional context about the use case or requirements
    type: text
    required: false
    ignore_undefined: true
    example: "For a SaaS product launch targeting small business owners"

  - name: output_type
    description: The desired type of output from the improved prompt
    type: select
    required: false
    ignore_undefined: true
    options:
      - creative
      - analytical
      - technical
      - conversational
      - structured
    default: structured
```

## Pattern Outputs

```yaml
results:
  - name: improved_prompt
    description: The optimized, well-defined prompt
    type: text
    required: true
    example: |
      You are an expert marketing copywriter specializing in SaaS product launches.

      Write a marketing email for a new SaaS product launch targeting small business owners.

      Requirements:
      - Subject line: Attention-grabbing, under 50 characters
      - Opening: Address a specific pain point small business owners face
      - Body: Highlight 3 key benefits of the product
      - Tone: Professional but approachable, conversational
      - Length: 200-300 words
      - Call-to-action: Clear next step (e.g., "Start your free trial")

      Format:
      - Subject line
      - Email body
      - CTA button text

      Avoid:
      - Overly salesy language
      - Technical jargon
      - Making unverified claims

  - name: improvement_notes
    description: Explanation of what was improved and why
    type: markdown
    required: true
    example: |
      ## Improvements Made

      1. **Added role context**: Specified "expert marketing copywriter" to set appropriate expertise level
      2. **Defined clear requirements**: Added specific constraints for subject line length, word count, and tone
      3. **Structured output format**: Specified exactly what sections should be included
      4. **Added constraints**: Listed what to avoid to prevent common issues
      5. **Clarified target audience**: Made explicit the small business owner focus
      6. **Specified key elements**: Broke down the email into measurable components (3 benefits, CTA, etc.)
```

## Model Configuration

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.5-sonnet
  temperature: 0.3
  max_tokens: 2000
  custom_parameters: {}
```
