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

> please build an ActiveModel API for Sidekiq Jobs

> Let's refactor the batch production pipeline. In particular: ... First, please write out a detailed design doc in a new Markdown file, that would be sufficient for a team of junior devs to implement the changes

> Please go ahead and begin the production pipeline refactor implementation. Start with the high-level structure, leaving NotImplementedError or whatever as appropriate, and we'll iteratively fill in the gaps

> Please proceed with the production pipeline refactor implementation. Start with the high-level structure, leaving NotImplementedError or whatever as appropriate, and then go through and iteratively fill in the gaps. Also, make sure to create unit and component tests as you go

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

> let's make this update the metrics in Firestore when the process starts up

> ok, so mow it updates when starting a job but not after finishing... let's just have it run update_metrics every 60 seconds in a loop

> let's override _perform_job in ApplicationJob to update the metrics

> processing time should be updated after each job, not every 60 seconds

> processing time should be updated at the end of the job when decrementing job count, not in the middlewhere

> let's run update_metrics every random(30,90) seconds

> let's add a healthcheck route at /health, and skip updating Firestore for calls to that

> ok, need to turn the sqlite column names from snake_case to camelCase

> let's make sure that the hash returned from the db is properly typed, in particular that properties is a hash and not just a string

> let's add a few lines to the logging config that keep track of the latest request time in Firestore. Use the default DB, collection "api_metrics", document "#{scope}", where scope = Rails.application.config_for("deploy").scope. don't initialize a new Firestore client every time. only try to talk to firestore if you don't see a K8S env var

> We are currently embedding docs one a time (well, all the chunks in each doc), storing in Elastic, and then importing to LanceDB. Let's instead create the embeddings in batched fashion, when the rest of the batch is ready (ie, in the callback), and store directly in LanceDB. In particular, we should query the db for all chunks attached to a batch, split into "partitions" of 25k chunks (we may assume that a batch's records and chunks are immutable, so we can simply keep track of the chunk id rank within the batch), and then for each partition we send the necessary data to a BatchedCreateEmbeddings sidekiq job, which uses PyCall.rb to call cohere embed on all the chunks (say 10 threads per sidekiq worker) and then store the results in LanceDB (in the same way that import_batch.py from the other repo stores them).

> Let's index the embeddings from Lance to Elastic in the `BatchedCreateEmbeddingsJob`; we can do this asynchronously, and at the end (after all the embeddings from the partitions are in both Lance and Elastic) run the callback for run_diagnostics

> in `index_to_elasticsearch`, let's use sidekiq to do this asynchronously, so that lance doesn't have to wait for Elastic; but do add it to a sidekiq batch shared with elastic indexing jobs from other `BatchedCreateEmbeddingsJob`s, so that we can run the diagnostic at the end of everything

> instead of sending all the chunks and embeddings to `ElasticIndexChunksJob`, just send the offsets so it can read everything from Lance; or add a "partition" column in Lance that indicates which `BatchedCreateEmbeddingsJob` and `ElasticIndexChunksJob` are responsible for each record

> instead of downloading the archive for nuix, let's just use gcsfuse, which is mounted with --implicit-dirs (and all buckets) at /mnt/gcs

> let's pass stdout and stderr from Nuix to the ruby process

> please make all the hard-coded configurations here (pubsubze inventory size etc) configurable via env var (but default to their current values)

> for docs without any DPs or chunks  (eg spreadsheets or movies), the ingestion process should mark as slipsheeted, and ingestion_status should check for that

> so in the embeddings callback we need to actually create the lance table, and also properly close it. We want the process to be restartable, see the attached .py files for how we have been doing it (we're taking Elastic out of the pipeline)

> so in the `BatchedCreateEmbeddingsJob` we need to actually create the lance table, and also properly close it. We want the process to be restartable, see the attached .py files for how we have been doing it (we're taking Elastic out of the pipeline)

> in processing_callback, when enqueuing all the batched embed jobs, we want to enqueue another job to call (either the actual code or the equivalent of) `close_batch_table`.py after adding all the records

> in processing_callback, when enqueuing all the batched embed jobs, we want to register another callback that runs (either the actual code throiugh PyCall.rb or the equivalent of) `close_batch_table`.py after adding all the records

> so we need the tags to be mapped not only fir the provided category_id, but also catrefs eith psrent_id equaling the provided id, in whixj case it should look for or create a new category eith the same name and the nrw parent id

> for "7z t", let's do the check for "Enter password" before the process completes

> hmm, that still didn't work, let's do a timeout after 30 seconds. Also, let's first check if we have a password, and only if we don't we should check if it needs one

> instead of df.apply, let's do a join in duckdb

> let's put the table from PG to Lance, and not copy it again if it's already loaded

> filename looks like this: 270-VOL054-1739929262490762.dat. Lets add another 3 columns for the batch_id, vol_number,production_date; and send to csv

> also, let's make it more killable with standard KeyboardInterrupt

> ah writing to Lance is taking forever since we're doing it one record at a time; should be in large batches (remember it's GCS); also make sure the whole process is idempotent

> let's make the rake tasks output to a logs dir; also, # bundle exec rake production_audit:recon:all

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

> wait, the middleware is not actually use, let's fix that

> hmm, getting an empty reply (no http response code) from the server; confirmed using curl

> hmm, logs show it's reading the sqlite db, but not adding any RDs to the batch...

> app/services/jobs/process_collection_batch/scrub_record_datum_json.rb:23:in `gsub!': can't modify frozen String: "185bbfcc-ad60-452d-8a00-f97c378dad74"

> same thing in return_nuix_metadata_json

> app/services/jobs/process_collection_batch/scrub_record_datum_json.rb:32:in `remove_properties_null_values': undefined method `each_pair' for ...

> app/services/jobs/process_collection_batch/return_nuix_metadata_json.rb:26:in `block in call': undefined method `translator' for ...

> app/services/jobs/process_collection_batch/return_nuix_metadata_json.rb:32:in `map!': can't modify frozen Array:

> app/services/jobs/process_collection_batch/return_record_datum_hash.rb:170:in `load_threading_values': More than one cluster thread index found for record: ... this didn't happen before (with the same data)

> there is no LnceSearch.batch_search, use the same methods as batch_import.py

> embeddings created isn't right

> Trying to call this, for some reason it's not showing any error but as you can see logging a status of "0", and the fragment sections are not created. Also the Rails.logging lines don't seem to be working...

> `/ask Traceback (most recent call last): duckdb.duckdb.ParserException: Parser Error: syntax error at or near "as"`

> duckdb.duckdb.InvalidInputException: Invalid Input Error: The quote option cannot exceed a size of 1 byte

> `/ask same error`

> `/ask hmm, where's that c3 coming from, can we strip it? python -c 'print(chr(0xfe))'|xxd`

> `/ask but it seems that chr(254) in both Python and duckdb returns multiple bytes... can we get just the 0xbe byte and use that as quote char?`

> `/ask still same error, and sameresult in Python # python -c 'print("\xBE")'|xxd`

> duckdb.duckdb.BinderException: Binder Error: Referenced column "bates_begin" not found in FROM clause!

> sh: 1: X-Amz-Credential=...: not found...

> SyntaxError: --> /mnt/shared/oz/app/lib/tasks/production_audit/reports/bates_range_report.rb

> NoMethodError: undefined method `[]' for nil:NilClass (NoMethodError)

> getting a lot of Error processing DAT content for batch 254 version 2025-01-31T16:34:02+00:00: Illegal quoting in line 1.; rather than trying top process the multibyte quote char, why don't you replace all thorns with a single-byte character and use that

> wait in production_audit.rb we're calling `process_dat_files` instead of `extract_dat_files`

> hmm seems to be hanging after the first 10 dats are written, any chance we forgot a `drain` or something?

> again seems to be stuck, during 7z, 7z processes are running but cpu is 0... do we need to make sure to actually read from 7z output?

> now all the dats are stuck at 0 (as opposed to a few KB), and there's only one 7z process, which still takes no cpu

> do we still need to drain or something?

> still stalling after writing some of the dats

> Error processing DAT files for batch 254: <class 'duckdb.duckdb.BinderException'>: Binder Error: Referenced table "v" not found!

> Error processing DAT files for batch 204: undefined method `len' for ...

> Error processing DAT files for batch 265: <class 'duckdb.duckdb.IOException'>: IO Error: No files found that match the pattern "/mnt/shared/oz/dats/265-VOL044 Supplement-*.dat" (need underscore); Error processing DAT files for batch 204: undefined method `compute' for ...

> hmm, something is doing substitution or something... Extracting with command: 7z x -so -p'h:T'(wb5l@.[KV/g+2-4'(wb5l@.[KV/g+2-4' ... Syntax error: "(" unexpected

> ActiveRecord::UnknownAttributeReference: Dangerous query method (method whose arguments are used as raw SQL) called with non-attribute argument(s): "nuix_metadata->>'md5'"

> PyCall::PyError: <class 'TypeError'>: connect(): incompatible function arguments. ... Invoked with: ':memory:'; kwargs: external_threads=False

> `app/app/models/sidekiq_job.rb:5:in \`<class:SidekiqJob>': uninitialized constant ActiveModel::Querying (NameError)`

> `app/models/sidekiq_job.rb:64:in \`from_job': can't convert String into an exact number (TypeError)`

> `app/models/sidekiq_job.rb:54:in \`new': wrong number of arguments (given 2, expected 1) (ArgumentError)`

> `app/models/sidekiq_job.rb:11:in \`columns': undefined method \`deduplicate' for ...`

> `app/models/sidekiq_job.rb:50:in \`all': abort then interrupt! (IRB::Abort)`

> `SidekiqJob has no table configured. Set one with SidekiqJob.table_name= (ActiveRecord::TableNotSpecified)`

> `PG::UndefinedTable: ERROR:  relation "sidekiq_jobs" does not exist (ActiveRecord::StatementInvalid)`

> `/app/app/models/sidekiq_job/connection_adapter.rb:1:in \`<main>': SidekiqJob is not a module (TypeError)`

> `/usr/local/bundle/gems/zeitwerk-2.6.14/lib/zeitwerk/loader/callbacks.rb:33:in \`on_file_autoloaded': expected file /app/app/models/sidekiq_job/connection_adapter.rb to define constant SidekiqJob::ConnectionAdapter, but didn't (Zeitwerk::NameError)`

> `/app/app/models/sidekiq_job/adapters/connection_adapter.rb:70: syntax error, unexpected end-of-input (SyntaxError)`

> NameError: uninitialized constant ProductionAudit::Recon (NameError)

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

> +Ok great, can you confirm just passing it that way will work? And I just need to give them the /auth/saml/metadata URL and they can download the cert?

> ok so we might as well remove the middleware and just do it in the job, right? Or is there some reason to have both?

> can we add a Sidekiq callback that runs `RunDiagnostic` after all the  `ElasticIndexChunksJob` for all partitions?

> that probably won't work, we need the `ElasticIndexChunksJob.perform_later` to run in `BatchedCreateEmbeddingsJob`, after the embeddings are in Lance (and not in processing_callback.rb; so we need to create the sidekiq batch in processing_callback.rb (as now) but then find it again (by batch.id) in `BatchedCreateEmbeddingsJob` and add jobs to it (that should be possible, right?)

> in batched_create_embeddings_job.rb, I believe we want to find the sidekiq batch using Thread.current[:sidekiq_batch]

> do we need to add a route, or is that already done somehow? How do I access lance search from frontend?

> 7z will successfully list the file without having the password, it just can't extract... maybe rather than swallowing stderr we check there? Or is there another way? Maybe 7z t?

> are yhose the attrivjres in thhe model?

> i mean, for Category?

> except isn't all of `load_record_datums` done before `produce_record_datums`?

> `/ask that's taking too long, can't we use windowing to speed it up? seems like it's n^2 rather than nlogn?`

> `/ask to verify this answer, let's look for bates begin/end inside these gaps: ...`

> `/ask now let's see ranges of bates numbers and which files they're in, eg from bates n to m all numbers appear in 1-vol33-555.dat, from m+1 to k they appear in both 2-vol34-666.dat and 2-vol34-667.dat, from k+1 to j they don't appear at all, etc`

> `/ask where are the audit reports`

> the reporting is looking at the copied zips, right?

> `/ask what do I need to do to make this accessible using .where etc, like ActiveRecord`

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

> +Actually, can you make the signature settings configurable (default false), and allow the cert and private key env vars to be null in the default case?

> +slipsheet is determined by there legitimately being no document pages

> +let's not change from GET to POST< since the code that uses this uses GET (not sure why, but annoying to change it now)

> +make it a one_liner using a wildcard

> +I have duckdb installed only through python tho

> `+assume path/to/dat is cwd`

> `/ask gimme date as %FT%T`

> `/ask can we encode it in sql rather than Python?`

> `/ask ok, duckdb is refusing to use thorn as quote... let's try just removing all the thorns`

> `\ask let's just use tr to remove thorns in the output`

> `/ask I just need start/end bates and \`files\`, and make sure to consolidate adjancent ranges with the same files`

> +let's disable sentry in this task. Also, need cache/keyera or store/keyera prefix Checking for production ZIP files...

> +ah looks like gcsfuse doesn't handle old versions. So first copy all the zips (serverside) to gs://tla-syllo-keyera-bucket/oz/productions/{batch_id}-{name}-{version timestamp}.zip

> +ah please continue

> +also would be nice to convert that to %FT%T for display, and/or to an actual date/time type for storage

> +it's actuall microseconds, not ms

> +let's use a more obscure/unlikely-to-be-actually-used character than | (but still one byte); also we need to escape it if it does appear

> +let's use duckdb wildcard functionality

> +duckdb can't handle multibyte quote chars, let's replace thorns with rs and use that

> +need to escape rs _before_ replacing `quote_char` with rs

> +we should only call `process_dat_files` once, after all the dats have been extracted

> +no, remember there can be multiple zips (different versions) for the same batch_id, and we want them all in

> +I mean speicifically where you do @table.delete

> +let's just use bash/system pipe/redirection rather than reimplementing it ourselves

> +instead of wildcards, let's specify the actual location of the dat in the zip, to avoid having to list

> +it's actually batchname/Data/batchname.DAT, eg VOL053/Data/VOL053.DAT

> +message is "Enter password"

> +for supplements it should be VOL049_Supplement/Data/VOL049_Supplement.DAT

> +for supplements it should be VOL049_Supplement/Data/VOL049_Supplement.DAT ( underscores rather than spaces)

> +please make sure in map_tags we actuallynuse the right attributes from the modrls

> +also makensure you're correcyly creating the chikd categories

> `+Hmm, this sort of works, but not in the same way as the usual models, eg SidekiqJob doesn't return the content, and SidekiqJob.all returns a list of SidekiqJobs which don't print as nicely as true ActiveRecord models; and .group doesn't work... Can't we make it an actual ActiveRecord model? But again, not backed by the usual db`

> `+Can't we generally do this by overriding some Connection object or something, rather than each of the ActiveRecord methods individually?`

> `+instead of .exec, can we use import_module('sys') and then append directly?`

> +we need to call (either the actual code or the equivalent of) `close_batch_table`.py after adding all the records

> +Do we actually need OpenStruct here? Also, no need to futher divide the embeddings batches when saving to Lance, 250*96 is fine to do in one call; also, let's make sure we actually send all the columns that we need to lance

> +let's add ../document-labeling instead of always at the root

> +ah but need to resolve the relative path, especially when checking

> +Sidekiq is also defined in rails server pods

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

> +ok, now let's set extra_workers for default to 0

> +please make this not override the env vars running Nuix

> +ah let's symbolize the keys

> +let's base.get_db_name() to get the Lance db_name (everywhere we need it)

> +need to provide the password to 7z

> +need to escape single-quotes in password

> +lookup by md5, fall back to filenames;

> +let's make import_batch sharded: * add a command that processes a particular shard, defined as id%n=i (use painless); * make import_batch spin up a statefulset or jobs with n pods that runs the import_shard command and cleans it up at the end

> +no need to set db_name explicitly, that should picked up automatically from the environment using base.get_db_name()

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

> `/ask now what's an actual oneliner, runnable from bash?`

> `/ask I have duckdb installed only through python tho; and I want a oneliner runnable from bash`

> `/ask now let's use another oneliner to verify it, also with duckdb csv functionality`

> `+let's find gaps in bates numbers (again, python/duckdb oneliner please`

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

> `+will ENV["PYTHONPATH"] work, or do we need the one in the sys module? goal is to get import document_labeling.whatever to work (document_labeling is a subdirectory of /document-labeling)`

> `+I'm trying to use pycall, and need to make sure it is only initialized by pycall_thread, not alone. How can I make sure that Rails doesn't 'require' it implicitly?`

> `+let's run this only when running sidekiq, not rails server (in particular, in rails server pods Python isn't available, so maybe detect that or rescue or something; or only run in sidekiq and rails console)`

## General Observations & Best Practices

*   **Context is King:** The user is diligent about providing context, whether it's through adding files (`/add`), pasting error messages, or describing the high-level goals.
*   **Iterative Process:** Development is a conversation, not a single command. The most successful interactions involve a back-and-forth of prompting, reviewing, and refining.
*   **Use the AI for Scaffolding:** The user frequently asks the AI to create initial designs, generate a list of ideas, or set up the structure for a new project.
*   **Combine AI with User Expertise:** The user doesn't blindly accept the AI's output. They review it, run tests, and provide expert guidance to correct its course, acting as a senior engineer overseeing a junior developer.
*   **Automate Everything:** There's a strong pattern of asking the AI to create scripts (`test.sh`, `deploy.sh`) to automate repetitive tasks like setup, testing, and deployment.
*   **Leverage AI for Analysis:** Beyond coding, the user frequently asks "why" questions to understand performance issues, design tradeoffs, and complex codebases.

By adopting these patterns, a developer can significantly enhance their productivity and use `aider` as a true collaborative partner.
