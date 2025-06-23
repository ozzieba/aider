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

> let's add a new ActiveRecord model for Sidekiq jobs, with appropriate columns etc, so that we can easily access it from rails c in the same way we access regular db models (but without actually using the db)

> {
> Let's refactor the batch production pipeline. In particular:
> - Let's vectorize, rather than doing everything one file (or even page) at a time
> - Let's do everything idempotently
> - Let's create new "stamped" RDs. Perhaps with a field that points to the original RD, rather than replacing the PDFs directly 
> - Let's automatically slipsheet anything that doesn't have document_data and document pages
> - Let's parallelize stamping across different pages of an RD
> First, please write out a detailed design doc in a new Markdown file
> }

> Ok, let's do this right. In particular, let's have real scripts in Ruby with PyCall.rb (in PyCallThread.run) to interact with Python and DuckDB. The goal is to audit every production we've run, its bates numbers, and RD id numbers. Note we're generally using GCS via the S3 API, and with versioning turned on; so we can see all the old versions of produced zips.

### 2. Implementation & Refactoring

These prompts are for making specific, significant changes to the codebase. They are more concrete than goal-setting prompts but still grant the AI autonomy to figure out the implementation details across multiple files.

**Annotation:** This is the core "coding" phase. The prompts clearly state *what* to do, but not necessarily *how* to do it. This is effective for tasks like integrating a new library, refactoring a component, or adding a new feature based on a pre-existing design.

**Examples:**

> let's add test coverage metrics

> please update the code in reviewer.py to use the firestore cache decorator from utils.py (instead of the existing firestore caching logic)

> So I'd like to add sp cert validation support to our SAML integration. The pod will have a relevant tls cert mounted, so we need to provide it through devise to omniauth/saml and turn on signing

> let's make import_batch sharded: * add a command that processes a particular shard, defined as id%n=i (use painless); * make import_batch spin up a statefulset or jobs with n pods that runs the import_shard command and cleans it up at the end

> let's make sure update_metrics runs at least once when the process starts up

> let's only do the the increment in the middleware, and the decrement in _perform; let's call the method update_processing_time; let's initialize the num eorkers etc to 0 if theyee uninitialized, and procesding time to 60.

> so Nuix is now returning data in a sqlite db (called metadata.db, table tiems), rather than a big json... Let's make the necessary changes here to read that data

> ok, now the sqlite database columns (as written by java for us to read) will have a prefix indicating type: n_ for numeric, s_ for string, b_ for boolean, d_ for date, and j_ for lists/hashes that should be JSON-parsed. Please update the logic accordingly

> I have the following frontend code that currently talks to Elastic. Let's add a Rails route to perform the search instead. ... And instead of using Elastic, let's use lance, like so...

> We are currently embedding docs one a time ... Let's instead create the embeddings in batched fashion, when the rest of the batch is ready (ie, in the callback), and store directly in LanceDB...

> let's turn the ingestion_status field on RecordDatum into a computed field, ie scope with_ingestion_status, which automatically checks for the presence of document_data, original_binary, document_pages (or slipsheet tag) , chunks, tokens,   etc. Should all be done DB-side

> let's replace `PyCallThread` with a multi-threaded version that does the following ...

> let's add auto retry with exponential backoff for cohere embed

### 3. Debugging & Troubleshooting

These are reactive prompts used when an error occurs. The user provides context about the failure (error messages, stack traces, symptoms) and asks for a fix.

**Annotation:** This pattern shows a tight feedback loop. The user runs code, observes a failure, and immediately feeds the context back to the AI. The phrase `"What's wrong? Fix"` is a recurring, efficient shorthand.

**Examples:**

> What's wrong? Fix

> tests failing on GH Actions: ... I think we need to install the Python libraries

> `[pasting a traceback]` please fix

> hmm, getting an empty reply (no http response code) from the server; confirmed using curl

> Doc-level Tagger seems to be incrementing twice per message a lot of the time, why would that be?

> Hmm, getting an error DEBUG -- omniauth: (saml) Request phase initiated. + ERROR -- omniauth: (saml) Authentication failure! no implicit conversion of nil into String: TypeError, no implicit conversion of nil into String

> we now have duplicate _perform_now methods

> this is bottlenecked on 'select * from record_data where id=$1', which is from line 409: "referent = ref_type.constantize.find(ref_id)"; let's fix this n+1

> weird getting Non-retryable HTTP status: 200 (Faraday::ClientError)

### 4. Code Analysis & Explanation

These prompts leverage the AI for code comprehension and analysis without requesting any code changes. This includes asking for architectural advice or exploring different implementation strategies.

**Annotation:** This is a powerful pattern for getting up to speed on an unfamiliar codebase, planning a refactor, or investigating performance issues. The user treats the AI as a consultant or a peer who can quickly analyze code and provide insights. The `/ask` command is often used for these types of questions.

**Examples:**

> Can you summarize the contents of this repo?

> How might you refactor this code?

> Please thoroughly analyze what happens when various components fail, and whether each document is indeed processed exactly once...

> why is extractMetadata so slow? In particular, why is it so much slower than the equivalent code in the old (non-`broker`) Main.java?

> is that redirect_to_new_user_registration_url implemented somewhere?

> /ask where are we parsing dates?

> /ask is there a good way to turn an arbitrary list/iterable/similar into an ActiveRecord connection adapter/model? Ie, be able to use the standard ActiveRecord interface (.where, .group, .columns) without actually talking to the db?

> /ask tell me more about NullDB

> /what's OPenStruct? why is it needed?

> /ask So 1461309 is a child of 1461426; when running produce on their batch, we get 1461309 produced twice, with different bates numbers, once on its own and once as a child of 1426; any idea why it didn't get skipped (since its parent was in the batch)?

> /ask I want to be able to think of all the data stores (GCS, filesystem, SQL, Elastic, Lance, sqlite...) as essentially caches of our immutable derivations. How can I express that in a way that works well with ActiveRecord and the above design? Show me different options and tradeoffs between them

### 5. Iterative Refinement & Clarification

This category captures the conversational nature of the interactions. The user provides course corrections, adds details, or refines a previous request.

**Annotation:** This is arguably the most important category. It highlights that AI-assisted development is a dialogue. The ability to refine and steer the AI is crucial for success. These prompts are often short and build on the immediate prior context.

**Examples:**

> not really what I meant, the code in reviewer.py is doing caching in firestore, I want to replace all that logic with the library function

> no, we need to create a new wrapper method that calls process_message, since process_message itself is overridden by the service-specific subclass

> much more detail please.

> actually, let's shard by message_id%100

> THat's not right, we want to be able to create new user dynamically from SAML info, as we were before

> actually, instead of searching by vector, let's search by text and do the embedding on the backend

> rather than explicit threads and mutexes, let's just use Parallel

> wait, why is this a concern? Let's make it conceptually a single relation

> no need to set db_name explicitly, that should picked up automatically from the environment, as in Python

### 6. Direct & Specific Instructions

These are small, tactical commands for precise changes. They leave little room for ambiguity.

**Annotation:** Use these prompts when you know exactly what needs to be changed and want to delegate the mechanical task of editing the code.

**Examples:**

> please add another script to reset a tagger...

> let's get the image from an env var

> make it also a cli arg

> For non-dev env, it should read $env.yaml and then default.yaml

> let's change the metrics_sources so that each source defaults a configurable value (default 0)

> use the k8s libraty, using in-cluster credentials

> let's add a TODO in the Batched Embed jobs to also send the embeddings to Elastic

> let's also sanitize all strings in the data bit, make sure everything is UTF8

> for `BatchedCreateEmbeddingsJob`, let's use in_threads: 10 rather than in_processes: `MAX_PROCESSES`

> let's round the time to the nearest 60 seconds, so it doesn't change more than once a minute and again the Firestore client should be initialized if and only if ENV['K8S'] exists (and its value will be "1")

### 7. Generating Documentation & Scripts

These prompts ask the AI to generate artifacts that are not production code, such as documentation, design docs, scripts, or presentations.

**Annotation:** This demonstrates the AI's utility beyond pure code generation. It can be used for the entire software development lifecycle, including planning, documentation, and creating helper scripts.

**Examples:**

> ...please skip the md and instead use the above directly to create a .org presentation viewable in html, including instructions on export

> please write a test script that finds the url and pw, uploads a gem, and downloads it

> Please write a detailed design doc for a new sidekiq-jruby service that can run Java jobs.

> please generate a pedagogic explanation of the code, how it's structured, what each part does, etc.

> please write a Python scrip that uses duckdb's read_csv to select all from a bunch of DAT's in a directory

> /ask now what's an actual oneliner, runnable from bash?

> let's write a new doc called "Lifecycle of a Record Datum Improvements", suggesting directions for improvement of our current system

### 8. Tooling & Environment Setup

This category includes prompts related to setting up the development, testing, and deployment environment. This includes Continuous Integration (CI) configuration, test harnesses, and managing dependencies.

**Annotation:** This shows the user leveraging the AI to manage the entire development lifecycle, including the operational aspects. Automating the setup and testing process is a common theme.

**Examples:**

> let's make tests spin up PG as needed. In particular, if there is no PG_URL or equivalent env var, we should spin up a docker container with pg. In GHA, we should use service containers and actually run rspec (in parallel with building and pushing the docker image)

> I'm trying to use pycall, and need to make sure it is only initialized by pycall_thread, not alone. How can I make sure that Rails doesn't 'require' it implicitly?

> will ENV["PYTHONPATH"] work, or do we need the one in the sys module? goal is to get import document_labeling.whatever to work (document_labeling is a subdirectory of /document-labeling)

> instead of chdir to /document-labeling, we need to add it to the python path... and we need to do it globally, maybe in a config initializer?

> please generate a script to store all the secrets in GCP secrets manager; also generally the dev project is syllo-6ce5

> Let's use a sqlite db or something for testing

## General Observations & Best Practices

*   **Context is King:** The user is diligent about providing context, whether it's through adding files (`/add`), pasting error messages, or describing the high-level goals.
*   **Iterative Process:** Development is a conversation, not a single command. The most successful interactions involve a back-and-forth of prompting, reviewing, and refining.
*   **Use the AI for Scaffolding:** The user frequently asks the AI to create initial designs, generate a list of ideas, or set up the structure for a new project.
*   **Combine AI with User Expertise:** The user doesn't blindly accept the AI's output. They review it, run tests, and provide expert guidance to correct its course, acting as a senior engineer overseeing a junior developer.
*   **Automate Everything:** There's a strong pattern of asking the AI to create scripts (`test.sh`, `deploy.sh`) to automate repetitive tasks like setup, testing, and deployment.
*   **Leverage AI for Analysis:** Beyond coding, the user frequently asks "why" questions to understand performance issues, design tradeoffs, and complex codebases.

By adopting these patterns, a developer can significantly enhance their productivity and use `aider` as a true collaborative partner.
