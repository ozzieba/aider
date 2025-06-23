# Aider Prompt Patterns and Best Practices

This document analyzes the `.aider.input.history` files to identify and categorize common prompt patterns used in successful AI-assisted development sessions. It serves as a guide for interacting effectively with `aider` and similar tools.

## Introduction

The interaction logs reveal a structured, conversational, and iterative approach to software development. The user acts as a senior engineer or architect, guiding the AI through high-level goals, detailed implementation, and debugging. The patterns below can be seen as a "playbook" for effective AI collaboration.

## Categories of Prompts

The prompts used can be broadly categorized into several distinct types, each serving a different purpose in the development lifecycle.

### 1. Goal Setting & Ideation

These prompts are used to kick off a new project or a significant new feature. They are typically high-level and open-ended, providing context and a broad objective. The user often performs a "brain dump" and asks the AI to structure the thoughts, create a plan, or generate initial design documents.

**Annotation:** This is the "blank page" phase. The key is to provide the AI with as much context as possible and then ask it to create a structured starting point. This leverages the AI's ability to organize information and outline a path forward.

**Examples:**

> so we need to plan a substantial rewrite of our document ingestion pipeline (context: eDiscovery). Let's plan a presentation on a set of proposals for the next few months. Please start by getting the following thoughts down into Markdown...

> let's design an interview for a senior backend softward engineer. The intervoew dhould bebstrictured as a troubleshooting/debugging exercisr, and sgoyld test skills in scripting, operations, log manipulation, as well as ttaditional backend skills. the candidate is most gamikiar with Python/DRF, so let's use that. Please statt by wriring down 10 ideas in a markdows file

> so we want to extend aider-chat... let's start by generating a design doc for our aider+ tool

### 2. Implementation & Refactoring

These prompts are for making specific, significant changes to the codebase. They are more concrete than goal-setting prompts but still grant the AI autonomy to figure out the implementation details across multiple files.

**Annotation:** This is the core "coding" phase. The prompts clearly state *what* to do, but not necessarily *how* to do it. This is effective for tasks like integrating a new library, refactoring a component, or adding a new feature based on a pre-existing design.

**Examples:**

> let's add test coverage metrics

> please update the code in reviewer.py to use the firestore cache decorator from utils.py (instead of the existing firestore caching logic)

> let's make import_batch sharded: * add a command that processes a particular shard, defined as id%n=i (use painless); * make import_batch spin up a statefulset or jobs with n pods that runs the import_shard command and cleans it up at the end

> let's make our tests independent of external pg, and instead use pg_tmp/ephemeralpg

### 3. Debugging & Troubleshooting

These are reactive prompts used when an error occurs. The user provides context about the failure (error messages, stack traces, symptoms) and asks for a fix.

**Annotation:** This pattern shows a tight feedback loop. The user runs code, observes a failure, and immediately feeds the context back to the AI. The phrase `"What's wrong? Fix"` is a recurring, efficient shorthand.

**Examples:**

> What's wrong? Fix

> tests failing on GH Actions: ... I think we need to install the Python libraries

> `[pasting a traceback]` please fix

> hmm, getting an empty reply (no http response code) from the server; confirmed using curl

> Doc-level Tagger seems to be incrementing twice per message a lot of the time, why would that be?

### 4. Code Analysis & Explanation

These prompts leverage the AI for code comprehension and analysis without requesting any code changes.

**Annotation:** This is a powerful pattern for getting up to speed on an unfamiliar codebase, planning a refactor, or investigating performance issues. The user treats the AI as a consultant or a peer who can quickly analyze code and provide insights.

**Examples:**

> Can you summarize the contents of this repo?

> How might you refactor this code?

> Please thoroughly analyze what happens when various components fail, and whether each document is indeed processed exactly once...

> why is extractMetadata so slow? In particular, why is it so much slower than the equivalent code in the old (non-`broker`) Main.java?

### 5. Iterative Refinement & Clarification

This category captures the conversational nature of the interactions. The user provides course corrections, adds details, or refines a previous request.

**Annotation:** This is arguably the most important category. It highlights that AI-assisted development is a dialogue. The ability to refine and steer the AI is crucial for success. These prompts are often short and build on the immediate prior context.

**Examples:**

> not really what I meant, the code in reviewer.py is doing caching in firestore, I want to replace all that logic with the library function

> no, we need to create a new wrapper method that calls process_message, since process_message itself is overridden by the service-specific subclass

> much more detail please.

> actually, let's shard by message_id%100

### 6. Direct & Specific Instructions

These are small, tactical commands for precise changes. They leave little room for ambiguity.

**Annotation:** Use these prompts when you know exactly what needs to be changed and want to delegate the mechanical task of editing the code.

**Examples:**

> please add another script to reset a tagger...

> let's get the image from an env var

> make it also a cli arg

> For non-dev env, it should read $env.yaml and then default.yaml

> let's change the metrics_sources so that each source defaults a configurable value (default 0)

### 7. Generating Documentation & Scripts

These prompts ask the AI to generate artifacts that are not production code, such as documentation, design docs, scripts, or presentations.

**Annotation:** This demonstrates the AI's utility beyond pure code generation. It can be used for the entire software development lifecycle, including planning, documentation, and creating helper scripts.

**Examples:**

> ...please skip the md and instead use the above directly to create a .org presentation viewable in html, including instructions on export

> please write a test script that finds the url and pw, uploads a gem, and downloads it

> Please write a detailed design doc for a new sidekiq-jruby service that can run Java jobs.

> please generate a pedagogic explanation of the code, how it's structured, what each part does, etc.

## General Observations & Best Practices

*   **Context is King:** The user is diligent about providing context, whether it's through adding files (`/add`), pasting error messages, or describing the high-level goals.
*   **Iterative Process:** Development is a conversation, not a single command. The most successful interactions involve a back-and-forth of prompting, reviewing, and refining.
*   **Use the AI for Scaffolding:** The user frequently asks the AI to create initial designs, generate a list of ideas, or set up the structure for a new project.
*   **Combine AI with User Expertise:** The user doesn't blindly accept the AI's output. They review it, run tests, and provide expert guidance to correct its course, acting as a senior engineer overseeing a junior developer.
*   **Automate Everything:** There's a strong pattern of asking the AI to create scripts (`test.sh`, `deploy.sh`) to automate repetitive tasks like setup, testing, and deployment.
*   **Leverage AI for Analysis:** Beyond coding, the user frequently asks "why" questions to understand performance issues, design tradeoffs, and complex codebases.

By adopting these patterns, a developer can significantly enhance their productivity and use `aider` as a true collaborative partner.
