# Aider Prompt Workflows

This document describes common workflows that emerge from sequences of prompts when using AI-assisted development tools like `aider`. These workflows are synthesized from the prompt patterns documented in `prompt_patterns.md`. They illustrate how a series of conversational turns can accomplish complex software development tasks, from initial design to implementation, debugging, and refactoring.

## Workflow 1: From Idea to Implementation

This workflow covers the entire lifecycle of a new feature, from a high-level concept to a working implementation. It typically starts with broad, open-ended ideation and progressively becomes more concrete.

### Step 1: Goal Setting and Design
The user provides a "brain dump" of a new idea and asks the AI to structure it into a plan or design document. This leverages the AI's ability to organize information and outline a path forward.

> so we need to plan a substantial rewrite of our document ingestion pipeline (context: eDiscovery). Let's plan a presentation on a set of proposals for the next few months. Please start by getting the following thoughts down into Markdown...

> Let's refactor the batch production pipeline. ... First, please write out a detailed design doc in a new Markdown file, that would be sufficient for a team of junior devs to implement the changes

### Step 2: Scaffolding the Implementation
Once the design is settled, the user asks the AI to begin implementation, starting with a high-level structure.

> Please go ahead and begin the production pipeline refactor implementation. Start with the high-level structure, leaving NotImplementedError or whatever as appropriate, and we'll iteratively fill in the gaps

### Step 3: Iterative Implementation
The core of the work happens here, with the user guiding the AI to fill in the implementation details. This often involves a tight loop of coding, testing, and refinement. The user might specify a methodology like TDD.

> Please proceed with the production pipeline rewrite implementation. Start with tests, and apply TDD methodlogy. ...

### Step 4: Debugging and Troubleshooting
As issues arise, the user provides error messages and stack traces, asking the AI for a fix. This is a highly reactive and tight feedback loop.

> `[pasting a traceback]` please fix

> hmm, logs show it's reading the sqlite db, but not adding any RDs to the batch...

### Step 5: Refinement and Course Correction
The user provides feedback to steer the AI's work, clarifying requirements or correcting misunderstandings.

> not really what I meant, the code in reviewer.py is doing caching in firestore, I want to replace all that logic with the library function

> +let's not change from GET to POST< since the code that uses this uses GET (not sure why, but annoying to change it now)

### Step 6: Finalization and Cleanup
Once the feature is working, the user may ask for cleanup tasks like removing stale comments or improving documentation.

> let's clean up old/unnecessary comments, particularly ones that document a change rather than the current status of the code

> please create a README.md with an overview of what this does, features, and detailed usage instructions, including passwords, escaping, nested archives, etc

## Workflow 2: Deep Dive Refactoring

This workflow focuses on improving an existing piece of code. It starts with analysis, moves to planning, and then executes the refactoring in small, verifiable steps.

### Step 1: Analysis and Strategy
The user asks the AI to analyze a piece of code and suggest improvements.

> let's refactor this file. optimize for readability, correcness-by-design, DRY, and general conciseness. Please give 7 different suggestions for how to reorganize the code, then decide on a overall architecture. Write the new architecture in a new markdown document

> How might you refactor this code?

### Step 2: Planning
Based on the analysis, the user and AI agree on a detailed, step-by-step plan. The emphasis is on breaking the work into small pieces to ensure tests pass at each stage.

> Please write a new document with a detailed, step-by-step plan for the refactor, with each step as small as possible while making progress and keeping the code working

> can we split this up in such a way that we have more frequent checkpoints where all the tests pass?

### Step 3: Incremental Execution and Validation
The user directs the AI to proceed with the plan, validating each step.

> please proceed with the refactor. at each step, mark your progress in the doc and let me know what commands to run for validation remember to prepend PYO3_PYTHON=/usr/bin/python3 when relevant, and if you run cargo use --manifest-path ext/pyrbrs/Cargo.toml. Let me know when you're done

> Please proceed with 2-4

### Step 4: Iterative Refinements
As the refactoring progresses, the user might adjust the plan or clarify instructions.

> let's revert these changes, keep Documentable#text_from_tokens the way it was

> I think we should rename from_files to `from_attachments`, and allow more general specification of which AR models/attachments to use... but also that's not really a stateless transformation, let's properly separate the separate and stateless parts; stateful part can be a service but not a transformation

## Workflow 3: Targeted Debugging Cycle

This workflow is a focused effort to find and fix a specific bug. It's characterized by a rapid, tight loop of information-gathering, hypothesis, and testing.

### Step 1: Problem Report
The user reports a bug, often with a stack trace, error message, or description of the incorrect behavior. The shorthand `"What's wrong? Fix"` is common.

> What's wrong? Fix

> `[pasting a traceback]` please fix

> Doc-level Tagger seems to be incrementing twice per message a lot of the time, why would that be?

### Step 2: The Fix Attempt
The AI proposes and implements a fix.

### Step 3: Verification
The user tests the fix. The cycle often continues as the first fix may not be correct or complete.

> hmm, that still didn't work, let's do a timeout after 30 seconds. Also, let's first check if we have a password, and only if we don't we should check if it needs one

> `/ask same error`

> umm now you broke nested file handling entirely...

### Step 4: Add Logging/Instrumentation
If the bug is elusive, the user asks the AI to add logging to get more information.

> Let's add some logging to figure out what the issue is

> hmm, still getting no real logs, I think it's not even getting to the callback

> ah can we actually see the tree in test output?

### Step 5: Resolution
The loop continues until the bug is fixed and verified.

## Workflow 4: Test-Driven Development (TDD) Cycle

This workflow follows the classic TDD "Red-Green-Refactor" cycle. It's often part of a larger implementation or refactoring workflow.

### Step 1: Write a Failing Test
The user asks the AI to write a test for a new piece of functionality. This can be a unit test, integration test, or even a property-based test.

> please proceed with the production pipeline rewrite implementation. Start with tests, and apply TDD methodlogy. ...

> great, now let's write actual tests for all these behaviors that can be run with bundle exec rake test

> let's create a comprehensive property-based testing suite for all functionality; however, for better readability etc let's use Ruby for the testing

### Step 2: Run the Test (Red)
The user (or AI) runs the test to confirm it fails as expected.

### Step 3: Write Code to Pass the Test (Green)
The AI writes the minimal code required to make the test pass.

### Step 4: Run Tests Again
All tests are run to confirm they now pass.

### Step 5: Refactor
With the safety of passing tests, the user can ask the AI to refactor the code for clarity or performance.

> can we make this more concise, eg using .and_then, and/or by introducting some option to the orchestrator to delete temp directories once we're done with them?

> let's make `GenerateRecordArtifacts` a bit more concise, in particular the actual logic of the core pipeline. eg move the particular config args to helper methods
