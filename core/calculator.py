import math
from scipy import stats

class SampleSizeCalculator:
    @staticmethod
    def calculate_proportions(p1, p2, alpha=0.05, power=0.8):
        """Calculate sample size for two-proportion z-test"""
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        p_pooled = (p1 + p2) / 2
        
        numerator = (z_alpha * math.sqrt(2 * p_pooled * (1 - p_pooled)) + 
                    z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2)))**2
        denominator = (p1 - p2)**2
        
        n = numerator / denominator
        return math.ceil(n)
    
    @staticmethod
    def calculate_continuous(mean1, mean2, std, alpha=0.05, power=0.8):
        """Calculate sample size for continuous metrics (t-test)"""
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        effect_size = abs(mean1 - mean2) / std
        n = 2 * ((z_alpha + z_beta) / effect_size)**2
        return math.ceil(n)
    
    @staticmethod
    def calculate_non_inferiority(p1, delta, alpha=0.05, power=0.8):
        """Calculate sample size for non-inferiority test"""
        z_alpha = stats.norm.ppf(1 - alpha)  # One-sided test
        z_beta = stats.norm.ppf(power)
        
        p2 = p1 - delta  # Non-inferiority margin
        p_pooled = (p1 + p2) / 2
        
        numerator = (z_alpha * math.sqrt(2 * p_pooled * (1 - p_pooled)) + 
                    z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2)))**2
        denominator = delta**2
        
        n = numerator / denominator
        return math.ceil(n)
    
    @staticmethod
    def estimate_runtime(sample_size, daily_users):
        """Estimate experiment runtime in days"""
        if daily_users > 0:
            return math.ceil(sample_size / daily_users)
        return 0 