# Branch 5 — Skill Contracts & Interfaces

**Purpose:** Define exact API contracts for B5 skills to enable agent-to-agent communication via OpenClaw.

---

## 1. ComfyUI Bridge Skill

### Skill Identity
```yaml
name: comfyui-bridge
version: 0.1.0
category: image-generation
provider: local
models: 
  - sdxl-juggernaut-xl
  - flux-dev-q6k
dependencies:
  - python:3.10+
  - websockets
  - aiohttp
platform: windows, linux, macos
```

### Function: `submit_generation_job`

**Purpose:** Queue image generation to ComfyUI, return job ID for polling

**Input Schema:**
```json
{
  "type": "object",
  "required": ["workflow_id", "prompt", "sampler", "steps"],
  "properties": {
    "workflow_id": {
      "type": "string",
      "description": "Template name from accounts/ACCOUNT/workflows/",
      "example": "portrait_v1_sdxl"
    },
    "prompt": {
      "type": "string",
      "description": "Full generation prompt (character description, style, mood)",
      "example": "A stern middle-aged man in wartime uniform, formal portrait, monochrome film grain, 1940s"
    },
    "negative_prompt": {
      "type": "string",
      "description": "What to avoid in generation",
      "example": "modern, cartoon, oversaturated color, blurry"
    },
    "sampler": {
      "type": "string",
      "enum": ["DPMSolverMultistep", "Euler", "Heun", "DDIM"],
      "description": "ComfyUI sampler algorithm",
      "default": "DPMSolverMultistep"
    },
    "cfg_scale": {
      "type": "number",
      "minimum": 1,
      "maximum": 20,
      "description": "Classifier-free guidance strength",
      "default": 7.5
    },
    "steps": {
      "type": "integer",
      "minimum": 10,
      "maximum": 50,
      "description": "Number of diffusion steps",
      "default": 20
    },
    "model": {
      "type": "string",
      "enum": ["sdxl-juggernaut-xl", "flux-dev-q6k"],
      "description": "Which model to use",
      "default": "sdxl-juggernaut-xl"
    },
    "lora": {
      "type": "array",
      "items": {"type": "string"},
      "description": "LoRA names to apply (from account config)",
      "example": ["FilmGrain_Redmond", "Monochrome_Halsman"]
    },
    "lora_weights": {
      "type": "array",
      "items": {"type": "number"},
      "description": "Strengths for each LoRA (0.0-1.0)",
      "example": [0.7, 0.9]
    },
    "seed": {
      "type": "integer",
      "description": "Random seed for reproducibility (null = random)",
      "example": null
    },
    "output_dir": {
      "type": "string",
      "description": "Where to save output images (relative to project root)",
      "default": "generated_images/"
    },
    "batch_size": {
      "type": "integer",
      "minimum": 1,
      "maximum": 4,
      "description": "Number of variations to generate",
      "default": 1
    },
    "timeout_sec": {
      "type": "integer",
      "minimum": 30,
      "maximum": 300,
      "description": "Max seconds to wait before aborting",
      "default": 120
    }
  }
}
```

**Output Schema (Success):**
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["queued", "submitted"],
      "description": "Job was accepted and queued"
    },
    "job_id": {
      "type": "string",
      "description": "Unique job identifier for polling",
      "example": "comfyui_job_20260326_143700_abc123"
    },
    "estimated_duration_sec": {
      "type": "number",
      "description": "Rough estimate of total time",
      "example": 18.5
    },
    "queue_position": {
      "type": "integer",
      "description": "Current position in ComfyUI queue",
      "example": 1
    },
    "polling_interval_sec": {
      "type": "integer",
      "description": "Recommended polling frequency",
      "example": 2
    }
  }
}
```

**Output Schema (Error):**
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["error", "invalid_input"],
      "description": "Job was rejected"
    },
    "error_code": {
      "type": "string",
      "enum": ["bad_workflow", "unsupported_model", "queue_full", "comfyui_offline"],
      "description": "Error category"
    },
    "error_message": {
      "type": "string",
      "description": "Human-readable error",
      "example": "Workflow 'portrait_v1_sdxl' not found in account config"
    },
    "remediation": {
      "type": "string",
      "description": "Suggested fix",
      "example": "Check account config at accounts/003_wwii/workflows.yaml"
    }
  }
}
```

---

### Function: `poll_generation_job`

**Purpose:** Check job status and retrieve results when done

**Input Schema:**
```json
{
  "type": "object",
  "required": ["job_id"],
  "properties": {
    "job_id": {
      "type": "string",
      "description": "Job ID from submit_generation_job",
      "example": "comfyui_job_20260326_143700_abc123"
    }
  }
}
```

**Output Schema (In Progress):**
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["queued", "executing"],
      "description": "Job is still running"
    },
    "progress": {
      "type": "number",
      "minimum": 0,
      "maximum": 100,
      "description": "Percent complete",
      "example": 45.5
    },
    "current_step": {
      "type": "integer",
      "description": "Which diffusion step (if known)",
      "example": 9
    },
    "elapsed_sec": {
      "type": "number",
      "description": "Time spent so far",
      "example": 8.3
    },
    "estimated_remaining_sec": {
      "type": "number",
      "description": "Predicted time to completion",
      "example": 9.7
    }
  }
}
```

**Output Schema (Completed):**
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["completed"],
      "description": "Job finished successfully"
    },
    "images": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "filename": {
            "type": "string",
            "description": "Output filename (relative to output_dir)",
            "example": "generation_0.png"
          },
          "path": {
            "type": "string",
            "description": "Full path to image",
            "example": "/c/Users/User-OEM/Desktop/content-factory/auto_content_factory/generated_images/vid_001_scene_03_0.png"
          },
          "width": {"type": "integer", "example": 768},
          "height": {"type": "integer", "example": 768},
          "size_bytes": {"type": "integer", "example": 245670}
        }
      },
      "description": "Generated images"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "seed_used": {
          "type": "integer",
          "description": "Actual seed (for reproducibility)",
          "example": 12345
        },
        "model_used": {
          "type": "string",
          "example": "sdxl-juggernaut-xl"
        },
        "loras_used": {
          "type": "array",
          "items": {"type": "string"},
          "example": ["FilmGrain_Redmond@0.7", "Monochrome_Halsman@0.9"]
        },
        "sampler_used": {"type": "string", "example": "DPMSolverMultistep"},
        "cfg_used": {"type": "number", "example": 7.5},
        "steps_used": {"type": "integer", "example": 20},
        "total_time_sec": {
          "type": "number",
          "description": "Total generation time",
          "example": 18.4
        },
        "vram_peak_gb": {
          "type": "number",
          "description": "Peak VRAM usage (if tracked)",
          "example": 10.2
        }
      }
    },
    "cost": {
      "type": "object",
      "properties": {
        "provider": {
          "type": "string",
          "enum": ["local_comfyui", "openrouter_fallback"],
          "example": "local_comfyui"
        },
        "cost_usd": {
          "type": "number",
          "description": "Cost of this job (0 for local)",
          "example": 0
        },
        "gpu_time_sec": {
          "type": "number",
          "example": 18.4
        }
      }
    }
  }
}
```

**Output Schema (Error):**
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["failed", "timeout", "cancelled"],
      "description": "Job did not complete"
    },
    "error_code": {
      "type": "string",
      "enum": ["out_of_memory", "generation_error", "cancelled_by_user", "timeout"],
      "description": "Failure reason"
    },
    "error_message": {
      "type": "string",
      "example": "CUDA out of memory: 12GB required, 10GB available"
    },
    "partial_output": {
      "type": "array",
      "description": "Any images generated before failure",
      "items": {"type": "string"}
    },
    "remediation": {
      "type": "string",
      "description": "How to fix or retry",
      "example": "Reduce batch_size to 1, or switch to Flux-Q4 (smaller)"
    }
  }
}
```

---

## 2. Image QA Skill

### Skill Identity
```yaml
name: image-qa
version: 0.1.0
category: quality-assurance
provider: anthropic, google
models:
  - claude-haiku
  - gemini-flash-lite
dependencies:
  - vision-capability
  - face-detection-library
platform: any
```

### Function: `evaluate_image`

**Purpose:** Score and validate image against criteria

**Input Schema:**
```json
{
  "type": "object",
  "required": ["image_path", "evaluation_type"],
  "properties": {
    "image_path": {
      "type": "string",
      "description": "Path to image file",
      "example": "/generated_images/vid_001_scene_03.png"
    },
    "evaluation_type": {
      "type": "string",
      "enum": ["portrait", "scene", "reference_photo"],
      "description": "Type of image being evaluated"
    },
    "expected_style": {
      "type": "string",
      "description": "Style reference (from account config)",
      "example": "monochrome_1940s_film_grain"
    },
    "character_spec": {
      "type": "object",
      "description": "Optional: character this portrait should match",
      "properties": {
        "name": {"type": "string", "example": "Winston Churchill"},
        "age_range": {"type": "string", "example": "60-70"},
        "key_features": {
          "type": "array",
          "items": {"type": "string"},
          "example": ["distinctive scowl", "cigar", "formal attire"]
        }
      }
    },
    "motion_intent": {
      "type": "boolean",
      "description": "Will this image be animated? (affects quality criteria)",
      "default": false
    },
    "min_score_threshold": {
      "type": "number",
      "minimum": 0,
      "maximum": 10,
      "description": "Minimum acceptable score (0-10)",
      "default": 7
    }
  }
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "image_path": {"type": "string"},
    "overall_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 10,
      "description": "Overall quality score",
      "example": 8.5
    },
    "verdict": {
      "type": "string",
      "enum": ["approved", "approved_with_notes", "review_manually", "rejected"],
      "description": "Decision (approved/rejected)"
    },
    "scores": {
      "type": "object",
      "properties": {
        "style_match": {
          "type": "number",
          "description": "How well does it match expected style?",
          "example": 9
        },
        "technical_quality": {
          "type": "number",
          "description": "Resolution, artifacts, compression",
          "example": 8
        },
        "aesthetic_quality": {
          "type": "number",
          "description": "Composition, lighting, color palette",
          "example": 8.5
        },
        "character_match": {
          "type": "number",
          "description": "Does portrait match character spec? (if applicable)",
          "example": 8
        },
        "motion_readiness": {
          "type": "number",
          "description": "Suitable for animation? (if motion_intent=true)",
          "example": 8
        }
      }
    },
    "flags": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "flag": {
            "type": "string",
            "enum": ["compression_artifact", "style_mismatch", "oversaturated", "undersaturated", "motion_hazard", "face_quality", "character_mismatch", "censored_content"],
            "example": "style_mismatch"
          },
          "severity": {
            "type": "string",
            "enum": ["info", "warning", "critical"],
            "example": "warning"
          },
          "description": {
            "type": "string",
            "example": "Color saturation slightly higher than expected for 1940s monochrome style"
          }
        }
      },
      "description": "Issues detected"
    },
    "remediation": {
      "type": "string",
      "description": "How to fix if rejected",
      "example": "Regenerate with sampler=Euler, cfg_scale=6.5 (less saturation)"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "dimensions": {
          "type": "string",
          "example": "768x768"
        },
        "file_size_mb": {
          "type": "number",
          "example": 0.24
        },
        "detected_faces": {
          "type": "integer",
          "description": "Number of faces detected (for portrait validation)",
          "example": 1
        },
        "evaluation_model": {
          "type": "string",
          "enum": ["haiku", "flash-lite", "ollama"],
          "example": "haiku"
        },
        "evaluation_time_sec": {
          "type": "number",
          "example": 2.3
        }
      }
    }
  }
}
```

---

## 3. Browser Animator Skill

### Skill Identity
```yaml
name: browser-animator
version: 0.1.0
category: animation
provider: freepik, higgsfield, selenium
models: none
dependencies:
  - selenium-webdriver
  - opencv-python
  - ffmpeg
platform: windows, linux, macos
```

### Function: `animate_image`

**Purpose:** Convert static image to animated video (img2video)

**Input Schema:**
```json
{
  "type": "object",
  "required": ["image_path", "audio_duration_sec"],
  "properties": {
    "image_path": {
      "type": "string",
      "description": "Path to image to animate",
      "example": "/approved_images/scene_03_portrait.png"
    },
    "audio_duration_sec": {
      "type": "number",
      "minimum": 0.5,
      "maximum": 30,
      "description": "Duration of audio this will sync with",
      "example": 3.5
    },
    "platform": {
      "type": "string",
      "enum": ["freepik", "higgsfield", "fallback_static"],
      "description": "Which img2video service to use",
      "default": "freepik"
    },
    "animation_config": {
      "type": "object",
      "description": "Animation style parameters",
      "properties": {
        "motion_type": {
          "type": "string",
          "enum": ["pan", "zoom", "rotation", "3d_look", "subtle"],
          "description": "Type of motion effect",
          "default": "subtle"
        },
        "intensity": {
          "type": "string",
          "enum": ["low", "medium", "high"],
          "description": "How pronounced the motion",
          "default": "medium"
        },
        "transition_in": {
          "type": "string",
          "enum": ["fade", "cut", "pan_in"],
          "description": "How scene enters",
          "default": "fade"
        },
        "transition_out": {
          "type": "string",
          "enum": ["fade", "cut", "pan_out"],
          "description": "How scene exits",
          "default": "fade"
        }
      }
    },
    "output_format": {
      "type": "string",
      "enum": ["mp4", "webm", "mov"],
      "description": "Video codec and container",
      "default": "mp4"
    },
    "output_dir": {
      "type": "string",
      "description": "Where to save output",
      "default": "animations/"
    },
    "timeout_sec": {
      "type": "integer",
      "minimum": 30,
      "maximum": 300,
      "description": "Max seconds to wait",
      "default": 120
    },
    "fallback_to_static": {
      "type": "boolean",
      "description": "If animation fails, return static frame?",
      "default": true
    }
  }
}
```

**Output Schema (Success):**
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["completed", "static_fallback"],
      "description": "Animation completed or fell back to static"
    },
    "animation_path": {
      "type": "string",
      "description": "Path to output video/image",
      "example": "/animations/scene_03_animated.mp4"
    },
    "duration_sec": {
      "type": "number",
      "description": "Actual output duration",
      "example": 3.5
    },
    "metadata": {
      "type": "object",
      "properties": {
        "codec": {
          "type": "string",
          "enum": ["h264", "vp9", "h265"],
          "example": "h264"
        },
        "resolution": {
          "type": "string",
          "example": "1080x1440"
        },
        "fps": {
          "type": "integer",
          "description": "Frames per second",
          "example": 24
        },
        "bitrate_mbps": {
          "type": "number",
          "example": 5.5
        },
        "file_size_mb": {
          "type": "number",
          "example": 2.4
        },
        "platform_used": {
          "type": "string",
          "enum": ["freepik_api", "higgsfield_api", "selenium_browser", "static_fallback"],
          "description": "Which service was actually used",
          "example": "freepik_api"
        },
        "generation_time_sec": {
          "type": "number",
          "example": 15.3
        }
      }
    },
    "cost": {
      "type": "object",
      "properties": {
        "platform_cost_usd": {
          "type": "number",
          "description": "Cost charged by Freepik/Higgsfield",
          "example": 0.50
        },
        "estimated_total_usd": {
          "type": "number",
          "example": 0.50
        }
      }
    }
  }
}
```

**Output Schema (Error):**
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["failed", "timeout"],
      "description": "Animation failed"
    },
    "error_code": {
      "type": "string",
      "enum": ["platform_unavailable", "invalid_image", "timeout", "api_error", "browser_crash"],
      "example": "timeout"
    },
    "error_message": {
      "type": "string",
      "example": "Freepik API did not respond within 120 seconds"
    },
    "fallback_status": {
      "type": "string",
      "enum": ["fallback_used", "fallback_disabled"],
      "description": "Whether static fallback was used",
      "example": "fallback_used"
    },
    "fallback_path": {
      "type": "string",
      "description": "If fallback used, path to static frame",
      "example": "/animations/scene_03_static.png"
    },
    "remediation": {
      "type": "string",
      "description": "How to recover",
      "example": "Check Freepik service status. Contact Lucca for manual intervention."
    }
  }
}
```

---

## 4. Image Director Brief Agent

### Agent Identity
```yaml
name: image_director_brief
role: Convert visual_plan → generation_request
model: claude-haiku or gpt-mini
model_config:
  temperature: 0.3
  max_tokens: 1000
```

### Input Format (from B3 visual_plan.json)
```json
{
  "scene_id": "001_03",
  "duration_sec": 4.2,
  "narrative": "Churchill addresses Parliament about the threat of Nazi invasion.",
  "mood": "tense, formal, wartime gravity, nationalistic resolve",
  "composition": {
    "framing": "wide_shot",
    "angle": "low_angle_heroic",
    "focal_point": "Churchill at podium",
    "lighting": "dramatic_side_lighting",
    "depth": "shallow_focus_on_speaker"
  },
  "characters": [
    {
      "name": "Winston Churchill",
      "emotion": "stern, resolute, commanding",
      "pose": "standing_at_podium",
      "age": "65",
      "clothing": "formal_wartime_uniform"
    }
  ],
  "setting": {
    "location": "House of Commons, Westminster, London",
    "era": "1940s, WWII era",
    "architectural_style": "gothic_revival",
    "time_of_day": "daytime_formal"
  },
  "visual_references": [
    "archive_photo_churchill_1940",
    "newsreel_parliament_session"
  ]
}
```

### Output Format (generation_request.json)
```json
{
  "request_id": "gen_req_001_03_20260326",
  "scene_id": "001_03",
  "image_type": "scene",
  "generation_type": "ai_synthetic",
  "account_id": "003_wwii",
  "prompt": "A formal wide-angle photograph of Winston Churchill addressing Parliament in 1940. Churchill stands at a wooden podium in the House of Commons chamber, shot from a low angle to convey authority and heroism. His face is stern and resolute, delivering a speech about invasion. The lighting is dramatic with strong side-lighting creating sharp shadows across his face. The background shows the gothic revival architecture of Westminster and attentive members of Parliament. The image has a monochrome film grain aesthetic characteristic of 1940s newsreel photography, with a slightly grainy texture and vintage color tone.",
  "negative_prompt": "modern, digital, oversaturated, CGI, cartoon, anime, blurry faces, modern clothing, contemporary setting, color photograph, bright lighting, cheerful mood, low resolution",
  "style_guidance": {
    "style_preset": "monochrome_1940s_film_grain",
    "tone": "formal, historic, dramatic",
    "era": "1940s",
    "photo_type": "newsreel_style_photograph"
  },
  "generation_params": {
    "sampler": "DPMSolverMultistep",
    "steps": 20,
    "cfg_scale": 7.5,
    "model": "sdxl-juggernaut-xl",
    "lora": ["FilmGrain_Redmond", "Monochrome_Halsman"],
    "lora_weights": [0.7, 0.9],
    "dimensions": {
      "width": 768,
      "height": 768
    }
  },
  "quality_requirements": {
    "min_score": 8.0,
    "focus_areas": ["face_clarity", "style_consistency", "composition"],
    "disqualifying_flags": ["oversaturated", "style_mismatch", "face_quality"]
  },
  "timing": {
    "scene_duration_sec": 4.2,
    "urgency": "normal"
  }
}
```

---

## 5. Image QA Agent

### Agent Identity
```yaml
name: image_qa_agent
role: Execute image-qa skill across batches
model: claude-haiku
batch_processing: true
concurrency: 5
```

### Workflow
```
receive: [image_paths] from image_generator
for each image:
  call: image-qa skill with appropriate criteria
  collect results
aggregate: approval rate, rejected list, remediation needed
output: image_qa_report.json
if approval_rate < threshold:
  flag to Production Manager for review
```

### Output Contract (image_qa_report.json)
```json
{
  "batch_id": "vid_001_batch",
  "timestamp": "2026-03-26T14:37:00Z",
  "account_id": "003_wwii",
  "images_total": 5,
  "summary": {
    "approved": 4,
    "approved_with_notes": 1,
    "review_manually": 0,
    "rejected": 0,
    "approval_rate": 1.0
  },
  "results": [
    {
      "image_id": "001_03_portrait",
      "image_path": "/generated_images/vid_001_scene_03_portrait.png",
      "qa_score": 8.5,
      "verdict": "approved",
      "scores": {
        "style_match": 9,
        "technical_quality": 8,
        "aesthetic_quality": 8.5,
        "character_match": 8,
        "motion_readiness": 8
      },
      "flags": [],
      "ready_for_animation": true,
      "evaluation_model": "haiku"
    }
  ],
  "statistics": {
    "avg_score": 8.5,
    "min_score": 8.0,
    "max_score": 9.0,
    "evaluation_time_sec": 14.2,
    "cost_usd": 0.08
  }
}
```

---

## Summary: Skill Dependencies

```
B3: visual_plan.json
    ↓
image_director_brief (Agent)
    ↓
generation_request.json
    ↓
image_generator (Agent)
    ↓ [calls comfyui-bridge skill]
    ↓
generated_images/
    ↓
image_qa_agent (Agent)
    ↓ [calls image-qa skill]
    ↓
image_qa_report.json
    ↓
[approved images]
    ↓
image_animator (Agent)
    ↓ [calls browser-animator skill]
    ↓
animations/ (mp4) or fallback static
    ↓
animation_output_spec.json
    ↓
B6: Scene Composition
```

**All contracts are VERSIONED.** Include `schema_version: "1.0"` in each JSON file for future compatibility.
