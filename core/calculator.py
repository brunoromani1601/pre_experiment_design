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
    def calculate_continuous_superiority(baseline_mean, expected_lift, std_dev, alpha=0.05, power=0.8):
        """Calculate sample size for continuous superiority test"""
        treatment_mean = baseline_mean + expected_lift
        return SampleSizeCalculator.calculate_continuous(baseline_mean, treatment_mean, std_dev, alpha, power)
    
    @staticmethod
    def calculate_continuous_non_inferiority(baseline_mean, margin, std_dev, alpha=0.05, power=0.8):
        """Calculate sample size for continuous non-inferiority test"""
        # For non-inferiority, we test if treatment is not worse than control by more than margin
        # H0: treatment_mean - baseline_mean <= -margin
        # H1: treatment_mean - baseline_mean > -margin
        z_alpha = stats.norm.ppf(1 - alpha)  # One-sided test
        z_beta = stats.norm.ppf(power)
        
        effect_size = margin / std_dev
        n = 2 * ((z_alpha + z_beta) / effect_size)**2
        return math.ceil(n)
    
    @staticmethod
    def calculate_non_inferiority(p1, delta, alpha=0.05, power=0.8):
        """Calculate sample size for non-inferiority test"""
        z_alpha = stats.norm.ppf(1 - alpha)  # One-sided test
        z_beta = stats.norm.ppf(power)
        
        # For non-inferiority, we test H0: p1 - p2 <= -delta vs H1: p1 - p2 > -delta
        # This is equivalent to testing H0: p2 - p1 >= delta vs H1: p2 - p1 < delta
        # So we use p1 as control and p1 - delta as treatment
        
        p2 = p1 - delta  # Treatment rate (non-inferiority margin)
        p_pooled = (p1 + p2) / 2
        
        numerator = (z_alpha * math.sqrt(2 * p_pooled * (1 - p_pooled)) + 
                    z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2)))**2
        denominator = delta**2
        
        n = numerator / denominator
        return math.ceil(n)
    
    @staticmethod
    def estimate_runtime(sample_size, daily_users):
        """Estimate experiment runtime in days"""
        if daily_users <= 0:
            return 0
        
        # Account for 50/50 traffic split between control and treatment
        # Each group needs sample_size users, so total needed = sample_size * 2
        total_sample_needed = sample_size * 2
        
        # Add 20% buffer for traffic fluctuations and incomplete data
        buffer_factor = 1.2
        adjusted_sample_needed = total_sample_needed * buffer_factor
        
        # Calculate days needed
        days_needed = adjusted_sample_needed / daily_users
        
        return math.ceil(days_needed) 