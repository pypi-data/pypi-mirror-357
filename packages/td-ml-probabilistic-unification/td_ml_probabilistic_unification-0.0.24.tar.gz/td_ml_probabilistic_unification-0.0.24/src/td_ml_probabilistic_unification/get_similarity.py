


# Similarity Calculation Module - Production Version

import pandas as pd
import numpy as np
import re
import logging
from similarity.jarowinkler import JaroWinkler
from similarity.cosine import Cosine
from similarity.normalized_levenshtein import NormalizedLevenshtein
from fuzzywuzzy import fuzz

# Initialize similarity objects
cosine = Cosine(2)
normalized_levenshtein = NormalizedLevenshtein()
jarowinkler = JaroWinkler()

logger = logging.getLogger(__name__)

def get_email_similarity(email_1, email_2):
    """Calculate email similarity using normalized Levenshtein distance"""
    if email_1 is None or email_2 is None or email_1 == '' or email_2 == '':
        return np.nan
    
    try:
        email_1 = str(email_1).split('@')[0].lower().strip()
        email_2 = str(email_2).split('@')[0].lower().strip()
        
        if not email_1 or not email_2:
            return np.nan
        
        distance = normalized_levenshtein.distance(email_1, email_2)
        return round(1 - distance, 2)
    except:
        return np.nan

def get_phone_similarity(phone_1, phone_2):
    """Calculate phone similarity using normalized Levenshtein distance"""
    if phone_1 is None or phone_2 is None or phone_1 == '' or phone_2 == '':
        return np.nan
    
    try:
        phone_1 = re.sub(r"\D", "", str(phone_1).strip())
        phone_2 = re.sub(r"\D", "", str(phone_2).strip())
        
        if not phone_1 or not phone_2:
            return np.nan
        
        # Handle different lengths
        if len(phone_1) != len(phone_2):
            if len(phone_1) > len(phone_2):
                phone_1 = phone_1[-len(phone_2):]
            else:
                phone_2 = phone_2[-len(phone_1):]
        
        distance = normalized_levenshtein.distance(phone_1, phone_2)
        return round(1 - distance, 2)
    except:
        return np.nan

def get_cosine_similarity(text_1, text_2):
    """Calculate cosine similarity"""
    if text_1 is None or text_2 is None or text_1 == '' or text_2 == '':
        return np.nan
    
    try:
        text_1 = str(text_1).lower().strip()
        text_2 = str(text_2).lower().strip()
        
        profile_1 = cosine.get_profile(text_1)
        profile_2 = cosine.get_profile(text_2)
        
        if not profile_1 or not profile_2:
            return np.nan
        
        similarity = cosine.similarity_profiles(profile_1, profile_2)
        return round(similarity, 2)
    except:
        return np.nan

def get_jarowinkler_similarity(text_1, text_2):
    """Calculate Jaro-Winkler similarity"""
    if text_1 is None or text_2 is None or text_1 == '' or text_2 == '':
        return np.nan
    
    try:
        text_1 = re.sub(r'[^A-Za-z0-9]+', ' ', str(text_1)).lower().strip()
        text_2 = re.sub(r'[^A-Za-z0-9]+', ' ', str(text_2)).lower().strip()
        
        if not text_1 or not text_2:
            return np.nan
        
        return jarowinkler.similarity(text_1, text_2)
    except:
        return np.nan

def get_fuzzy_similarity(text_1, text_2):
    """Calculate fuzzy token sort ratio similarity"""
    if text_1 is None or text_2 is None or text_1 == '' or text_2 == '':
        return np.nan
    
    try:
        text_1 = re.sub(r'[^A-Za-z0-9]+', ' ', str(text_1)).lower().strip()
        text_2 = re.sub(r'[^A-Za-z0-9]+', ' ', str(text_2)).lower().strip()
        
        if not text_1 or not text_2:
            return np.nan
        
        ratio = fuzz.token_sort_ratio(text_1, text_2)
        return round(ratio / 100.0, 2)
    except:
        return np.nan

def calculate_weighted_similarity(sim_data, sim_feat_list, weights, min_coverage=0.5):
    """Calculate weighted similarity with proper handling of missing values"""
    
    if sim_data.empty:
        return pd.Series(dtype=float)
    
    # Check if features exist
    missing_features = [feat for feat in sim_feat_list if feat not in sim_data.columns]
    if missing_features:
        logger.warning(f"Missing similarity features: {missing_features}")
        return pd.Series([0.0] * len(sim_data), index=sim_data.index)
    
    sim_features = sim_data[sim_feat_list].copy()
    
    # Count non-null features for each row
    valid_features = ~sim_features.isnull()
    coverage = valid_features.sum(axis=1) / len(sim_feat_list)
    
    # Apply coverage filter
    insufficient_coverage = coverage < min_coverage
    
    # Calculate weighted scores
    weighted_scores = []
    weights_array = np.array(weights)
    
    for idx, (_, row) in enumerate(sim_features.iterrows()):
        if insufficient_coverage.iloc[idx]:
            weighted_scores.append(0.0)
        else:
            try:
                valid_mask = ~row.isnull()
                
                if not valid_mask.any():
                    weighted_scores.append(0.0)
                    continue
                
                # Calculate normalized weights for available features
                available_weights = weights_array[valid_mask]
                
                if len(available_weights) == 0 or np.sum(available_weights) == 0:
                    weighted_scores.append(0.0)
                    continue
                
                normalized_weights = available_weights / np.sum(available_weights)
                available_similarities = row[valid_mask].values
                
                # Filter out NaN similarities
                valid_similarities = ~np.isnan(available_similarities)
                if not np.any(valid_similarities):
                    weighted_scores.append(0.0)
                    continue
                
                final_similarities = available_similarities[valid_similarities]
                final_weights = normalized_weights[valid_similarities]
                
                # Renormalize weights
                if np.sum(final_weights) > 0:
                    final_weights = final_weights / np.sum(final_weights)
                    weighted_score = np.sum(final_similarities * final_weights)
                    weighted_score = max(0.0, min(1.0, weighted_score))
                    weighted_scores.append(weighted_score)
                else:
                    weighted_scores.append(0.0)
                    
            except Exception as e:
                weighted_scores.append(0.0)
    
    return pd.Series(weighted_scores, index=sim_data.index)

def get_similarities(sim_data, feature_dict, string_type='jarowinkler', min_coverage=0.5):
    """Calculate similarities based on feature dictionary"""
    
    logger.info(f"Calculating similarities for {len(sim_data)} pairs")
    
    if sim_data.empty:
        raise ValueError("Input data is empty")
    
    if not feature_dict:
        raise ValueError("Feature dictionary is empty")
    
    sim_feat_list = []
    col_names = []
    weights = []
    
    # Similarity function mapping
    string_similarity_functions = {
        'jarowinkler': get_jarowinkler_similarity,
        'cosine': get_cosine_similarity,
        'fuzzy': get_fuzzy_similarity
    }
    
    # Process each feature
    for feature in feature_dict:
        name = feature['name']
        feature_type = feature['type']
        weight = float(feature['weight'])
        
        col_names.append(name)
        weights.append(weight)
        sim_feat_name = f"{name}_sim"
        sim_feat_list.append(sim_feat_name)
        
        # Check if columns exist
        col1 = f"{name}_1"
        col2 = f"{name}_2"
        
        if col1 not in sim_data.columns or col2 not in sim_data.columns:
            logger.warning(f"Columns {col1} or {col2} not found")
            sim_data[sim_feat_name] = np.nan
            continue
        
        # Calculate similarities based on feature type
        try:
            if feature_type == 'email':
                similarity_func = get_email_similarity
            elif feature_type == 'phone':
                similarity_func = get_phone_similarity
            elif feature_type == 'string':
                similarity_func = string_similarity_functions.get(string_type, get_jarowinkler_similarity)
            else:
                logger.warning(f"Unknown feature type '{feature_type}', using Jaro-Winkler")
                similarity_func = get_jarowinkler_similarity
            
            sim_data[sim_feat_name] = sim_data[[col2, col1]].apply(
                lambda x: similarity_func(x.iloc[0], x.iloc[1]), axis=1
            )
            
        except Exception as e:
            logger.error(f"Error calculating similarities for feature '{name}': {e}")
            sim_data[sim_feat_name] = np.nan
    
    # Normalize weights
    total_weight = sum(weights)
    if total_weight == 0:
        weights = [1.0 / len(weights)] * len(weights)
    elif total_weight != 1.0:
        weights = [w / total_weight for w in weights]
    
    # Calculate weighted similarity
    sim_data['score'] = calculate_weighted_similarity(sim_data, sim_feat_list, weights, min_coverage)
    
    # Add coverage information
    valid_features = ~sim_data[sim_feat_list].isnull()
    sim_data['feature_coverage'] = valid_features.sum(axis=1) / len(sim_feat_list)
    
    logger.info(f"Similarity calculation completed - mean score: {sim_data['score'].mean():.3f}")
    
    return sim_data, sim_feat_list, col_names, weights