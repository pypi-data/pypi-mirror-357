# 🗂️ TaskDaily

A flexible and dynamic daily task management system that helps you organize and track your daily tasks across unlimited projects.

## Features

- 📝 Create daily task files with customizable templates
- 🔄 Smart task carrying forward (excludes completed tasks)
- 🎯 Dynamic project support with emoji prefixes
- 🎨 Customizable task status workflow
- 📤 Multiple output formats (Slack, Teams, WhatsApp, Email)
- ⚙️ User-specific configuration management
- 🔒 Safe configuration handling with defaults

## Installation

```bash
pip install taskdaily
```

To update to the latest version:
```bash
pip install --upgrade taskdaily
```

## Quick Start

1. Initialize configuration (first time only):
```bash
daily config init
```

2. Create today's task file:
```bash
daily create
```

3. Share your daily plan/report:
```bash
# Share daily plan (default: Slack format)
daily share

# Share EOD report
daily share --report

# Share in different formats
daily share --format slack
daily share --format teams
daily share --format whatsapp
daily share --format email
```

## Project Management

Projects are dynamically managed using emoji prefixes. Simply start a section with an emoji:

```markdown
🏠 Personal
- [ ] Buy groceries ⚡
- [ ] Call dentist 🚧

💼 Work
- [ ] Review PR #123 ✅
- [ ] Debug issue #456 ⚡

📚 Learning
- [ ] Study Python ✅
```

You can create unlimited projects with any emoji prefix!

## Task Status Management

Tasks are managed through status emojis in your daily markdown files. To change a task's status, simply edit the emoji at the end of the task line.

The default status workflow is:
- 📝 Planned (excluded from reports)
- ⚡ In Progress
- 🚧 Blocked
- 📅 Rescheduled
- ➡️ Carried Forward
- ✅ Completed (not carried forward)
- 🚫 Cancelled

Example of changing task status:
```markdown
# Original task
- [ ] Review documentation 📝

# Change to in-progress
- [ ] Review documentation ⚡

# Mark as completed
- [ ] Review documentation ✅
```

Status behaviors:
- Tasks marked as ✅ (completed) won't carry forward to the next day
- Tasks marked as 🚫 (cancelled) won't carry forward
- Tasks with 📝 (planned) status are excluded from EOD reports
- All other tasks will carry forward with ➡️ status

## Output Formats

TaskDaily supports multiple output formats:

### Slack
```bash
daily share --format slack
```
- Proper emoji codes (e.g., :memo:)
- Clean bullet points (○ for todo, ● for done)
- Section dividers

### Microsoft Teams
```bash
daily share --format teams
```
- Markdown formatting
- Proper headers
- Task checkboxes (☐, ☑)

### WhatsApp
```bash
daily share --format whatsapp
```
- Bold headers
- Simple formatting
- Unicode bullets

### Email
```bash
daily share --format email
```
- HTML formatting
- Clean lists
- Professional layout

## Configuration

The package uses a configuration file located at `~/.config/daily-task/config.yaml`. You can:

- Reset to defaults: `daily config init`
- View config paths: `daily config path`

### Customizing Status Workflow

Add or modify statuses in your config file:
```yaml
status:
  planned:
    name: "Planned"
    emoji: "📝"
    show_in_report: false
    carry_forward: true
  in_progress:
    name: "In Progress"
    emoji: "⚡"
    show_in_report: true
    carry_forward: true
  completed:
    name: "Completed"
    emoji: "✅"
    show_in_report: true
    carry_forward: false
  # Add more statuses...
```

## Smart Features

1. Task Handling:
   - Completed tasks (✅) are not carried forward
   - Planned tasks (📝) are excluded from EOD reports
   - Tasks maintain their status when carried forward

2. Project Management:
   - Create unlimited projects
   - Use any emoji as project prefix
   - No configuration needed for new projects

3. Format Handling:
   - Each format has optimized styling
   - Preserves emojis and formatting
   - Maintains readability across platforms

## Testing

For detailed testing instructions and guidelines, see [TESTING.md](TESTING.md).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

- **Nainesh Rabadiya** - [GitHub](https://github.com/nainesh-rabadiya)
- Email: nkrabadiya@gmail.com

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
