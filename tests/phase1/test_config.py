"""Tests for configuration overrides."""

from anse.config import ANSEConfig, get_config, set_config

def test_get_and_set_config():
    # Test getting default
    cfg = get_config()
    assert isinstance(cfg, ANSEConfig)
    
    # Test setting custom config
    custom_cfg = ANSEConfig()
    custom_cfg.seed = 999
    set_config(custom_cfg)
    
    # Test it persisted
    assert get_config().seed == 999
    
    # Reset
    set_config(cfg)
