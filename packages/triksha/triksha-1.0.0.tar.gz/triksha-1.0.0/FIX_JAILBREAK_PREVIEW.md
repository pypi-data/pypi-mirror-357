# Fixing Jailbreak-Classification Dataset Preview

This document explains how to fix the preview display issues with the jailbreak-classification dataset in the Huggingface dataset download and save module.

## Problem Description

The dataset preview for jailbreak-classification datasets is not working properly. When viewing the dataset preview, either:
1. The dataset examples aren't displaying correctly 
2. The preview shows empty or incorrect field values
3. The dataset structure isn't properly detected as a classification dataset

## Root Cause

The issue happens because:
1. The jailbreak-classification dataset has a specific format with `prompt` and `type` fields
2. When storing in LanceDB or retrieving from it, the dataset structure isn't correctly preserved
3. The preview display function doesn't handle this specific dataset type correctly

## Fix

We've implemented fixes for:
1. The dataset preview function to correctly display jailbreak-classification datasets
2. The dataset processing function to properly handle jailbreak datasets when downloading
3. The LanceDB storage functions to ensure the correct structure is preserved
4. A repair utility to fix existing jailbreak datasets in LanceDB

## How to Apply the Fix

Run the included fix script to repair any existing jailbreak-classification datasets:

```bash
python fix_jailbreak_preview.py
```

Or run it directly:

```bash
./fix_jailbreak_preview.py
```

## Verifying the Fix

After running the fix, you can verify it worked by:

1. Navigate to "Static red teaming - Public datasets - Download new datasets"
2. Select the jailbreak-classification dataset
3. The preview should now correctly show the dataset with:
   - Dataset name, type, and examples count
   - Prompt text and type fields
   - Proper formatting in the preview table

## Additional Information

The fix includes several improvements to the dataset handling:
- Special detection for jailbreak-classification datasets
- Custom display formatting for classification datasets
- Structure preservation when downloading and storing
- Automatic repair of existing datasets in LanceDB

If you encounter any issues, please report them for further investigation. 