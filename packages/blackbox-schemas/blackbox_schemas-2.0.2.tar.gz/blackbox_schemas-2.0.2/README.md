# BlackBox Schemas

A Python package providing consolidated Pydantic v2 models for BlackBox LLM operations.

## Installation

1. Install the package:
   ```bash
   pip install blackbox-schemas
   ```

2. Use the models in your code:
   ```python
    #!/usr/bin/env python3

    # Test importing from blackbox_schemas
    try:
        # Import directly from the models module
        from blackbox_schemas.models import CategoryEvaluation, RFPEvaluation, Recommendation, SubmissionDetails
        print("Successfully imported models from blackbox_schemas.models")
        
        # Create test instances
        technical_category = CategoryEvaluation(
            category="Technical",
            pros_cons={
                "Pros": ["Clear requirements", "Standard technology"],
                "Cons": ["Short timeline"]
            },
            feasibility="High",
            observations=["Well documented"],
            recommendations=["Proceed with caution"]
        )
        
        legal_category = CategoryEvaluation(
            category="Legal",
            pros_cons={
                "Pros": ["Standard terms", "Clear compliance requirements"],
                "Cons": ["Strict liability clauses"]
            },
            feasibility="Medium",
            observations=["Some complex legal requirements"],
            recommendations=["Legal review needed"]
        )
        
        recommendation = Recommendation(
            decision="Go",
            summary="Project is technically feasible with manageable legal risks",
            next_steps=["Assemble technical team", "Schedule legal review", "Prepare timeline"]
        )
    
        submission_details = SubmissionDetails(
            due_date="2023-12-15",
            submission_type="online",
            submission_details="Submit via email to proposals@example.com",
            submission_instructions="Send as a single PDF file, maximum 20MB. Include company name in filename."
        )
        
        # Create the full RFP evaluation
        rfp_eval = RFPEvaluation(
            evaluation=[technical_category, legal_category],
            recommendation=recommendation,
            timeline_and_submission_details=submission_details
        )
        
        # Test serialization/deserialization
        print("\n✅ Full RFP Evaluation:")
        json_data = rfp_eval.model_dump_json(indent=2)
        print(f"\nJSON output: {json_data}")
        
        # Test recreating from dict
        print("\n✅ Recreating from dict:")
        recreated = RFPEvaluation.model_validate_json(json_data)
        print(f"Recreated evaluation has {len(recreated.evaluation)} categories")
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    ```