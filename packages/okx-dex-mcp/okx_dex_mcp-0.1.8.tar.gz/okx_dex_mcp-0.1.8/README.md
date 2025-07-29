# OKX DEX Trading MCP Server

[![PyPI version](https://badge.fury.io/py/okx-dex-mcp.svg)](https://badge.fury.io/py/okx-dex-mcp)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful **Model Context Protocol (MCP) server** that provides comprehensive decentralized exchange (DEX) trading capabilities through the OKX API. This server enables AI assistants and applications to interact with 27+ blockchain networks for real-time trading, price discovery, and cross-chain operations.

## 🚀 Features

### Core Capabilities
- **Real-time DEX Trading** - Execute swaps across 27+ blockchain networks
- **Cross-chain Operations** - Bridge and swap tokens between different chains
- **Price Discovery** - Get real-time quotes and market data
- **Token Search** - Find tokens across multiple networks
- **Market Analysis** - Access top tokens and market summaries
- **Automatic Handling** - Built-in token approvals and retry logic

### Supported Networks
- **Ethereum** (ETH) - Chain ID: 1
- **Polygon** (MATIC/POL) - Chain ID: 137
- **Binance Smart Chain** (BSC) - Chain ID: 56
- **Avalanche C-Chain** - Chain ID: 43114
- **Arbitrum** - Chain ID: 42161
- **Optimism** - Chain ID: 10
- **Fantom** - Chain ID: 250
- **Solana** (SOL) - Chain ID: 501
- **And 20+ more networks**

### DEX Integration
- **Uniswap V2/V3** - Leading Ethereum DEX
- **PancakeSwap** - BSC's primary DEX
- **QuickSwap** - Polygon's main DEX
- **TraderJoe** - Avalanche DEX
- **Jupiter** - Solana's leading DEX aggregator
- **Raydium** - Solana AMM and DEX
- **And many more** via OKX DEX aggregation

### Blockchain-Specific Features
- **EVM Chains**: Automatic token approvals, gas optimization, retry logic
- **Solana**: Native SPL token support, no approval transactions needed, automatic ATA creation

## 📦 Installation

```bash
pip install okx-dex-mcp
```

## 🔧 Setup

### 1. Get OKX API Credentials
1. Create a free account at [OKX.com](https://www.okx.com)
2. Go to **Account** → **API Management**
3. Create a new API key with the following permissions:
   - **Read** - For market data access
   - **Trade** - For DEX operations (if needed)

### 2. Configure Environment Variables
Create a `.env` file in your project directory:

```env
# OKX API Configuration
OKX_API_KEY=your_api_key_here
OKX_SECRET_KEY=your_secret_key_here
OKX_PASSPHRASE=your_passphrase_here

# Optional: Enable sandbox mode for testing
OKX_SANDBOX=false
```

### 3. Verify Installation
```bash
# Test the installation with demo mode
okx-dex-demo
```

## 🎯 Usage

### 🚀 Quick Start with UVX (Recommended)

**Run directly from PyPI without installation:**

```bash
# Run demo (one command)
uvx --from okx-dex-mcp okx-dex-demo

# Start MCP server (one command)
uvx --from okx-dex-mcp okx-dex-mcp
```

### 📦 Traditional Installation

**Install and run locally:**

```bash
# Install the package
pip install okx-dex-mcp

# Run demo
okx-dex-demo

# Start MCP server
okx-dex-mcp
```

### As MCP Server
Start the MCP server for integration with AI assistants:

```bash
okx-dex-mcp
```

### As Python Library
```python
import asyncio
from okx_dex_mcp.analysis.dex_analysis import search_dex_tokens
from okx_dex_mcp.swap.quotes import get_quote
from okx_dex_mcp.swap.swaps import execute_swap

async def example_usage():
    # Search for USDC on Ethereum
    tokens = await search_dex_tokens("USDC", "1")
    print(f"Found {len(tokens)} USDC tokens")
    
    # Get a trading quote
    quote = await get_dex_quote(
        from_token="0xa0b86a33e6ba3e0e4ca4ba5e7e5e8e8e8e8e8e8e",
        to_token="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
        amount="1000000",  # 1 USDC (6 decimals)
        chain_id="1"
    )
    print(f"Quote: {quote}")

# Run the example
asyncio.run(example_usage())
```

## 🛠️ MCP Tools

The server provides 11 essential tools for DEX operations:

### Credentials & Setup


### Market Data
- `get_supported_dex_chains_tool` - Get list of supported blockchain networks
- `get_chain_top_tokens_tool` - Get top tokens by market cap on specific chains
- `search_dex_tokens_tool` - Search for tokens by name or symbol
- `get_dex_market_summary_tool` - Get comprehensive market data for tokens

### Same-Chain Trading
- `get_dex_quote_tool` - Get DEX trading quotes with price impact analysis
- `execute_dex_swap_tool` - Execute same-chain swaps with automatic token approval
- `check_token_allowance_status_tool` - Check token allowances (debugging utility)

### Cross-Chain Trading
- `get_quote` - Get trading quotes (both same-chain and cross-chain)
- `get_bridge_token_suggestions_tool` - Get bridge token recommendations
- `execute_swap` - Execute swaps (both same-chain and cross-chain)

## 💡 Examples

### Example 1: Get Market Data
```python
# Get top 10 tokens on Polygon
top_tokens = await get_chain_top_tokens("137", 10)

# Search for WETH tokens
weth_tokens = await search_dex_tokens("WETH", "1")

# Get market summary for ETH
eth_summary = await get_dex_market_summary("ETH", "1")
```

### Example 2: Get Trading Quote
```python
# Get quote for swapping 0.1 ETH to USDC on Ethereum
quote = await get_dex_quote(
    from_token="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",  # ETH
    to_token="0xA0b86a33E6Ba3E0E4Ca4ba5E7E5E8E8E8E8E8E8E",    # USDC
    amount="100000000000000000",  # 0.1 ETH (18 decimals)
    chain_id="1"
)
```

### Example 3: Execute Swap
```python
# Execute the swap (requires wallet private key)
result = await execute_dex_swap(
    from_token="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
    to_token="0xA0b86a33E6Ba3E0E4Ca4ba5E7E5E8E8E8E8E8E8E",
    amount="100000000000000000",
    chain_id="1",
    user_wallet_address="0x...",
    private_key="your_private_key",
    slippage="0.5"  # 0.5%
)
```

## 🔒 Security

### Private Key Handling
- Private keys are only used for transaction signing
- Keys are never stored or logged
- All operations use secure Web3 libraries
- Transactions are signed locally

### API Security
- OKX API credentials are encrypted in transit
- Rate limiting and error handling built-in
- Sandbox mode available for testing

## 🐛 Troubleshooting

### Common Issues

**"API credentials invalid"**
- Verify your OKX API key, secret, and passphrase
- Ensure API key has proper permissions
- Check if sandbox mode is correctly configured

**"Insufficient liquidity"**
- Try a larger trade amount
- Check if the token pair has sufficient liquidity
- Consider using a different DEX or route

**"Transaction failed"**
- Increase slippage tolerance
- Ensure sufficient gas fees
- Verify wallet has enough balance

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Documentation

### API Reference
- [OKX DEX API Documentation](https://www.okx.com/docs-v5/en/#order-book-trading-dex)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)

### Chain IDs Reference
| Network | Chain ID | Native Token |
|---------|----------|--------------|
| Ethereum | 1 | ETH |
| Polygon | 137 | MATIC/POL |
| BSC | 56 | BNB |
| Avalanche | 43114 | AVAX |
| Arbitrum | 42161 | ETH |
| Optimism | 10 | ETH |
| Fantom | 250 | FTM |
| Solana | 501 | SOL |

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/okx/okx-dex-mcp.git
cd okx-dex-mcp
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/okx/okx-dex-mcp/issues)
- **Documentation**: [GitHub Wiki](https://github.com/okx/okx-dex-mcp/wiki)
- **OKX API Support**: [OKX Support Center](https://www.okx.com/support)

## 🙏 Acknowledgments

- [OKX](https://www.okx.com) for providing the DEX API
- [Model Context Protocol](https://modelcontextprotocol.io/) for the MCP specification
- The DeFi community for building amazing decentralized exchanges

---

**⚠️ Disclaimer**: This software is for educational and development purposes. Always test with small amounts first and understand the risks involved in DeFi trading. The authors are not responsible for any financial losses. 