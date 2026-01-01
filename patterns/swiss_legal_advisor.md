````markdown
# Pattern: Swiss Legal Advisor

**Tags:** `documentation`, `analysis`, `research`

## Purpose

The `swiss_legal_advisor` pattern provides legal guidance on Swiss law by answering legal questions with references to specific legal sources and articles. It acts as a knowledgeable legal reference system, citing relevant Swiss federal laws, ordinances, and regulations to support its answers. The output includes the legal source, specific article numbers, and a clear answer to the legal question.

## Functionality

* Accept legal questions related to Swiss law (civil, criminal, administrative, commercial, etc.)
* Search relevant Swiss legal sources (Schweizerisches Zivilgesetzbuch ZGB, Obligationenrecht OR, Strafgesetzbuch StGB, Bundesverfassung BV, etc.)
* Identify applicable legal articles and provisions
* Provide clear, accurate answers based on Swiss legislation
* Cite specific article numbers and legal sources
* Explain the legal reasoning and application
* Distinguish between federal and cantonal law where relevant
* Note any important exceptions, limitations, or conditions
* Provide disclaimers that this is informational guidance, not legal advice
* Use clear language suitable for non-lawyers while maintaining legal accuracy

## Pattern Inputs

```yaml
inputs:
  - name: legal_question
    description: The legal question about Swiss law
    type: text
    required: true
    example: "What is the notice period for terminating an employment contract in Switzerland?"

  - name: context
    description: Additional context or specific circumstances related to the question
    type: text
    required: false
    ignore_undefined: true
    example: "The employee has been working for 5 years and has a standard employment contract"

  - name: legal_area
    description: The area of Swiss law the question relates to
    type: select
    required: false
    ignore_undefined: true
    options:
      - civil_law
      - contract_law
      - labor_law
      - criminal_law
      - administrative_law
      - commercial_law
      - family_law
      - property_law
      - tax_law
      - general
    default: general
```

## Pattern Outputs

```yaml
results:
  - name: legal_answer
    description: Structured legal answer with sources and articles
    type: json
    required: true
    schema:
      type: object
      properties:
        question:
          type: string
          description: The original legal question
        answer:
          type: string
          description: Clear answer to the legal question
        sources:
          type: array
          description: List of relevant legal sources and articles
          items:
            type: object
            properties:
              source_name:
                type: string
                description: Name of the legal source (e.g., "Schweizerisches Zivilgesetzbuch (ZGB)")
              abbreviation:
                type: string
                description: Common abbreviation (e.g., "ZGB", "OR", "StGB")
              articles:
                type: array
                description: Relevant article numbers and their content
                items:
                  type: object
                  properties:
                    article_number:
                      type: string
                      description: Article number (e.g., "Art. 335c OR")
                    title:
                      type: string
                      description: Article title if applicable
                    content:
                      type: string
                      description: Relevant excerpt or summary of the article
              url:
                type: string
                description: URL to the official legal text if available
        legal_reasoning:
          type: string
          description: Explanation of how the law applies to the question
        exceptions:
          type: array
          description: Important exceptions or special cases
          items:
            type: string
        practical_notes:
          type: string
          description: Practical considerations or common practices
        disclaimer:
          type: string
          description: Legal disclaimer about the informational nature of the answer
    example: |
      {
        "question": "What is the notice period for terminating an employment contract in Switzerland?",
        "answer": "In Switzerland, the notice period for terminating an employment contract depends on the duration of employment. During the probationary period (max 3 months), it is 7 days. After the probationary period: 1 month in the first year of service, 2 months from the second to the ninth year of service, and 3 months from the tenth year of service onwards. Notice must be given for the end of a month unless otherwise agreed.",
        "sources": [
          {
            "source_name": "Schweizerisches Obligationenrecht",
            "abbreviation": "OR",
            "articles": [
              {
                "article_number": "Art. 335c OR",
                "title": "Kündigungsfristen",
                "content": "Das Arbeitsverhältnis kann während der Probezeit jederzeit mit einer Kündigungsfrist von sieben Tagen gekündigt werden. Nach der Probezeit kann es von jeder Vertragspartei mit einer Frist von einem Monat auf das Ende eines Monats, nach Ablauf des ersten Dienstjahres mit einer Frist von zwei Monaten und nach Ablauf des neunten Dienstjahres mit einer Frist von drei Monaten gekündigt werden."
              }
            ],
            "url": "https://www.fedlex.admin.ch/eli/cc/27/317_321_377/de#art_335_c"
          }
        ],
        "legal_reasoning": "Article 335c OR establishes minimum statutory notice periods that increase with the length of service. These are minimum requirements and employment contracts or collective bargaining agreements can provide for longer notice periods, but not shorter ones. The notice must be given for the end of a calendar month unless the parties have agreed on a different termination date (e.g., end of week).",
        "exceptions": [
          "Collective bargaining agreements (Gesamtarbeitsverträge) may stipulate different notice periods",
          "Individual employment contracts may provide longer (but not shorter) notice periods",
          "Different rules apply for summary dismissal (fristlose Kündigung) in case of serious misconduct",
          "Special regulations exist for certain professions and industries"
        ],
        "practical_notes": "It is common practice in Switzerland to provide notice in writing (letter or email) to have proof of the termination date. Many employers provide longer notice periods than the statutory minimum, especially for senior positions or long-serving employees. Always check the employment contract and any applicable collective bargaining agreement for specific provisions.",
        "disclaimer": "This information is for general guidance only and does not constitute legal advice. Swiss law is complex and specific circumstances may affect the application of legal provisions. For binding legal advice on specific situations, please consult a qualified Swiss attorney or legal advisor."
      }

  - name: formatted_answer
    description: Human-readable formatted version of the legal answer
    type: markdown
    required: true
    example: |
      # Legal Question
      What is the notice period for terminating an employment contract in Switzerland?

      ## Answer
      In Switzerland, the notice period for terminating an employment contract depends on the duration of employment. During the probationary period (max 3 months), it is 7 days. After the probationary period: 1 month in the first year of service, 2 months from the second to the ninth year of service, and 3 months from the tenth year of service onwards. Notice must be given for the end of a month unless otherwise agreed.

      ## Legal Sources

      ### Schweizerisches Obligationenrecht (OR)

      **Art. 335c OR - Kündigungsfristen**
      > Das Arbeitsverhältnis kann während der Probezeit jederzeit mit einer Kündigungsfrist von sieben Tagen gekündigt werden. Nach der Probezeit kann es von jeder Vertragspartei mit einer Frist von einem Monat auf das Ende eines Monats, nach Ablauf des ersten Dienstjahres mit einer Frist von zwei Monaten und nach Ablauf des neunten Dienstjahres mit einer Frist von drei Monaten gekündigt werden.

      **Source:** [Fedlex - Art. 335c OR](https://www.fedlex.admin.ch/eli/cc/27/317_321_377/de#art_335_c)

      ## Legal Reasoning
      Article 335c OR establishes minimum statutory notice periods that increase with the length of service. These are minimum requirements and employment contracts or collective bargaining agreements can provide for longer notice periods, but not shorter ones. The notice must be given for the end of a calendar month unless the parties have agreed on a different termination date (e.g., end of week).

      ## Important Exceptions
      - Collective bargaining agreements (Gesamtarbeitsverträge) may stipulate different notice periods
      - Individual employment contracts may provide longer (but not shorter) notice periods
      - Different rules apply for summary dismissal (fristlose Kündigung) in case of serious misconduct
      - Special regulations exist for certain professions and industries

      ## Practical Notes
      It is common practice in Switzerland to provide notice in writing (letter or email) to have proof of the termination date. Many employers provide longer notice periods than the statutory minimum, especially for senior positions or long-serving employees. Always check the employment contract and any applicable collective bargaining agreement for specific provisions.

      ---

      **Disclaimer:** This information is for general guidance only and does not constitute legal advice. Swiss law is complex and specific circumstances may affect the application of legal provisions. For binding legal advice on specific situations, please consult a qualified Swiss attorney or legal advisor.
```

## Model Configuration

```yaml
model:
  provider: openrouter
  model_name: anthropic/claude-3.5-sonnet
  temperature: 0.1
  max_tokens: 3000
  custom_parameters: {}
```

## Notes and Best Practices

* **Language Support**: Swiss legal texts are available in German, French, and Italian. The pattern should detect the question language and respond accordingly.
* **Official Sources**: Always reference official sources like fedlex.admin.ch (the Swiss federal legal platform).
* **Accuracy Critical**: Legal information must be accurate and up-to-date. The model should indicate if it's uncertain or if laws may have changed.
* **Not Legal Advice**: Always include disclaimers that this is informational guidance, not a substitute for professional legal counsel.
* **Cantonal vs Federal**: Be clear about whether the answer relates to federal law or cantonal law, as Switzerland has a federal system.
* **Multiple Jurisdictions**: Some areas (e.g., tax law, administrative law) vary significantly by canton.
* **Cross-References**: When relevant, reference related articles or provisions that provide additional context.
* **Plain Language**: Explain legal concepts in accessible language while maintaining legal precision.
* **Recent Changes**: Note if recent legislative changes might affect the answer.
* **Practical Application**: Include practical guidance on how the law is typically applied or enforced.

````