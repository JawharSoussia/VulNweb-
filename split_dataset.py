"""Create train/val/test splits for malicious_phish dataset (60/20/20)"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os

# Load the dataset
df = pd.read_csv('data/raw/malicious_phish.csv')
print(f"Original dataset shape: {df.shape}")
print(f"\nClass distribution before split:")
print(df['type'].value_counts())
print(f"\nClass proportions before split:")
print((df['type'].value_counts(normalize=True) * 100).round(2))

# Create directories if they don't exist
os.makedirs('data/train', exist_ok=True)
os.makedirs('data/val', exist_ok=True)
os.makedirs('data/test', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

# Split: 60% train, 20% val, 20% test (stratified by class)
train_df, temp_df = train_test_split(df, test_size=0.4, random_state=42, stratify=df['type'])
val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df['type'])

print(f"\nTrain split: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
print(f"Val split: {len(val_df)} ({len(val_df)/len(df)*100:.1f}%)")
print(f"Test split: {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")

# Verify class distribution is preserved
print(f"\n--- TRAIN CLASS DISTRIBUTION ---")
print(train_df['type'].value_counts())
print(f"\n--- VAL CLASS DISTRIBUTION ---")
print(val_df['type'].value_counts())
print(f"\n--- TEST CLASS DISTRIBUTION ---")
print(test_df['type'].value_counts())

# Save splits
train_df.to_csv('data/train/train.csv', index=False)
val_df.to_csv('data/val/val.csv', index=False)
test_df.to_csv('data/test/test.csv', index=False)

print("\n✅ Splits created and saved successfully:")
print("   - data/train/train.csv")
print("   - data/val/val.csv")
print("   - data/test/test.csv")
