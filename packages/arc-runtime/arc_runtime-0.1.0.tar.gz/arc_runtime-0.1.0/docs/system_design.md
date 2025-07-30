<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arc V1 Architecture</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #ffffff;
            color: #000000;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #000000;
            margin-bottom: 30px;
            font-size: 2.2em;
        }
        #diagram-container {
            background: #ffffff;
            border: 2px solid #000000;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
        }
        .mermaid {
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Arc V1: CI/CD for AI Reliability</h1>
        
        <div id="diagram-container">
            <div class="mermaid">
graph TD
    subgraph "Customer Environment"
        CustomerAgent[Customer Agent<br/>BlackRock/PANW]
        ArcRuntime[Arc Runtime<br/>Request Interceptor<br/>Model Cache<br/>~500 lines Python]
        LocalCache[(Local Model<br/>Cache<br/>Latest LoRA)]
    end

    subgraph "Arc V1 Core - Performance Optimized"
        Collector[High-Speed Collector<br/>gRPC endpoint<br/>Streaming ingestion]
        
        subgraph "Real-time Analysis"
            FailureDetector[Failure Detector<br/>Pattern matching<br/>Bloom filters<br/>less than 1ms detection]
            TaxonomyDB[(Failure Taxonomy<br/>Redis + PostgreSQL<br/>Hot/Cold storage)]
            PriorityQueue[Priority Queue<br/>High-impact failures first]
            FailureRate[Failure Rate Monitor<br/>Tracks decline<br/>15% to 5% to 1%]
        end
        
        subgraph "Reward Generation & Validation"
            RewardGen[Reward Generator<br/>PCGRLLM-style<br/>Tree-of-Thought<br/>For new patterns]
            VerifiableValidator[Verifiable Validator<br/>Binary 0/1 validation<br/>JSON/API/Code checks<br/>less than 1s validation<br/>No human labels]
            RewardCache[(Reward Cache<br/>Verified functions<br/>by failure type<br/>Arc's growing moat)]
            DataPrep[Smart Preprocessor<br/>Deduplication<br/>Importance sampling]
        end
        
        subgraph "Synthetic Data Engine"
            SyntheticGen[Synthetic Failure Generator<br/>Positive + Negative examples<br/>8x performance gain<br/>Activates at less than 5% failure rate]
            FailureMixer[Failure Mixer<br/>Real:Synthetic ratio<br/>Dynamic adjustment]
        end
        
        subgraph "Trinity-RFT Training"
            Explorer[Trinity Explorer<br/>Cached rollouts<br/>Parallel envs]
            Buffer[Prioritized Buffer<br/>Impact-weighted<br/>sampling]
            Trainer[Efficient Trainer<br/>LoRA/QLoRA<br/>Gradient checkpointing<br/>Mixed precision]
        end
        
        ModelRegistry[Model Registry<br/>S3 + CloudFront CDN<br/>Versioned LoRA adapters<br/>A/B test configs]
        
        subgraph "Deployment Pipeline"
            Validator[Auto Validator<br/>Deterministic checks<br/>Regression tests<br/>Performance metrics]
            Deployer[Progressive Deployer<br/>Canary to 10% to 50% to 100%]
        end
    end

    CustomerAgent -->|1. Request| ArcRuntime
    ArcRuntime -->|2a. Check cache| LocalCache
    LocalCache -->|2b. If pattern matches<br/>INTERCEPT and FIX| CustomerAgent
    ArcRuntime -->|3. Log all traces<br/>async, non-blocking| Collector
    
    Collector -->|4. Stream processing| FailureDetector
    FailureDetector -->|5a. Known patterns| TaxonomyDB
    FailureDetector -->|5b. Prioritized failures| PriorityQueue
    FailureDetector -->|5c. Track rate| FailureRate
    
    PriorityQueue -->|6a. New patterns| RewardGen
    PriorityQueue -->|6b. Known patterns| RewardCache
    RewardGen -->|7. Validate reward| VerifiableValidator
    VerifiableValidator -->|8a. If valid 0/1| RewardCache
    VerifiableValidator -->|8b. If valid| DataPrep
    RewardCache -->|9. Cached reward| DataPrep
    
    FailureRate -->|10. If less than 5% failures| SyntheticGen
    SyntheticGen -->|11. Generated failures| FailureMixer
    DataPrep -->|12a. Real failures| FailureMixer
    FailureMixer -->|12b. Mixed dataset| Explorer
    
    Explorer -->|13. Efficient rollouts| Buffer
    Buffer -->|14. Weighted sampling| Trainer
    
    Trainer -->|15. LoRA weights<br/>every 2 hours| Validator
    Trainer -.->|15b. Feedback on<br/>reward quality| RewardGen
    Validator -->|16. If performance OK| Deployer
    Deployer -->|17. Progressive rollout| ModelRegistry
    
    ModelRegistry -->|18. CDN push<br/>~1 min| LocalCache
    ModelRegistry -.->|18b. Successful rewards| RewardCache
    
    TaxonomyDB -.->|Real-time metrics| CustomerAgent
    
    classDef newFeature fill:#cccccc,stroke:#000000,stroke-width:3px
    class VerifiableValidator,SyntheticGen newFeature
            </div>
        </div>
    </div>
    
    <script>
        mermaid.initialize({ 
            theme: 'neutral',
            themeVariables: {
                primaryColor: '#ffffff',
                primaryTextColor: '#000000',
                primaryBorderColor: '#000000',
                lineColor: '#000000',
                secondaryColor: '#f0f0f0',
                tertiaryColor: '#e0e0e0',
                background: '#ffffff',
                mainBkg: '#ffffff',
                secondBkg: '#f8f8f8',
                clusterBkg: '#f5f5f5',
                clusterBorder: '#000000',
                fontSize: '14px'
            },
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis',
                rankSpacing: 70,
                nodeSpacing: 40
            }
        });
    </script>
</body>
</html>