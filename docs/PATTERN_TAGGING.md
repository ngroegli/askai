# Pattern Tagging System

## Overview

The pattern tagging system allows patterns to be categorized and filtered using tags. Tags are defined in a central YAML configuration file and can be used with the `-lp`, `-vp`, and `-up` command-line parameters to filter patterns.

## Tag Categories

Tags are organized into six categories:

1. **domain** - The problem domain or field of application
   - `data-analysis`, `security`, `development`, `documentation`, `content`, `market-research`, `operations`

2. **type** - The type of task or operation
   - `generation`, `analysis`, `transformation`, `summarization`, `visualization`

3. **use_case** - Common use cases or scenarios
   - `troubleshooting`, `reporting`, `automation`, `research`, `monitoring`, `web-development`

## Usage

### Listing All Tags

```bash
askai --list-tags
```

This displays all available tags organized by category with descriptions.

### Filtering Patterns by Tags

```bash
# List patterns with specific tags
askai -lp --tag security --tag analysis

# List patterns matching "data-analysis" tag
askai -lp --tag data-analysis

```

When multiple tags are provided, patterns matching ANY of the tags will be displayed (OR logic).

### Viewing Pattern Tags

When listing patterns, tags are displayed alongside each pattern:

```bash
askai -lp

Available patterns:
----------------------------------------------------------------------
ID: data_visualization 📦
Name: Data Visualization
Source: built-in
Tags: data-analysis, visualization, visualization, reporting
----------------------------------------------------------------------
```

## Adding Tags to Patterns

Tags are added to pattern markdown files on the second line after the title:

```markdown
# Pattern: My Pattern Name

**Tags:** `domain-tag`, `type-tag`, `input-tag`, `output-tag`, `complexity-tag`, `use-case-tag`

## Purpose
...
```

### Example

```markdown
# Pattern: Log Interpretation

**Tags:** `security`, `analysis`, `log`, `report`, `troubleshooting`

## Purpose
...
```

## Tag Definitions

Tags are defined in `config/pattern_tags.yml`. Each tag has:

- **id**: The unique identifier used in pattern files
- **name**: The human-readable name
- **description**: A brief description of when to use this tag

### Example Tag Definition

```yaml
tags:
  domain:
    - id: security
      name: Security
      description: Security operations, threat detection, and analysis
```

## Implementation Details

### Pattern Manager Methods

- `list_patterns(tags: Optional[List[str]] = None)` - List patterns, optionally filtered by tags
- `get_all_tags()` - Get all tag definitions organized by category
- `get_tags_for_pattern(pattern_id: str)` - Get tags for a specific pattern

### CLI Parameters

- `-lp --tag [TAGS...]` / `--list-patterns [TAGS...]` - List patterns, optionally filtered by tags
- `--list-tags` - List all available tags

## Best Practices

1. **Use Multiple Tags**: Apply 4-6 tags per pattern covering different categories
2. **Be Specific**: Choose tags that accurately describe the pattern's purpose
3. **Consider Users**: Think about how users might search for this pattern
4. **Update Tags**: Review and update tags when pattern functionality changes
5. **Consistent Naming**: Follow the naming convention in tags.yml

## Future Enhancements

Potential future improvements to the tagging system:

- AND logic for tag filtering (match all tags instead of any)
- Tag aliases for common search terms
- Tag hierarchies or relationships
- Pattern recommendations based on tag similarity
- Tag usage statistics and popular tag combinations
