// Blockchain Balance Screener Application

// Application State
const AppState = {
  currentAnalysis: null,
  transactions: [],
  filteredTransactions: [],
  currentPage: 1,
  transactionsPerPage: 10,
  sortField: 'date',
  sortDirection: 'desc',
  charts: {}
};

// Blockchain Data (Expanded with Etherscan V2 support)
const blockchains = {
  ethereum: { name: 'Ethereum', symbol: 'ETH', color: '#627EEA', decimals: 18 },
  polygon: { name: 'Polygon', symbol: 'MATIC', color: '#8247E5', decimals: 18 },
  bsc: { name: 'BNB Smart Chain', symbol: 'BNB', color: '#F3BA2F', decimals: 18 },
  arbitrum: { name: 'Arbitrum', symbol: 'ETH', color: '#28A0F0', decimals: 18 },
  optimism: { name: 'Optimism', symbol: 'ETH', color: '#FF0420', decimals: 18 },
  avalanche: { name: 'Avalanche', symbol: 'AVAX', color: '#E84142', decimals: 18 },
  base: { name: 'Base', symbol: 'ETH', color: '#0052FF', decimals: 18 },
  blast: { name: 'Blast', symbol: 'ETH', color: '#FCFC03', decimals: 18 },
  linea: { name: 'Linea', symbol: 'ETH', color: '#121212', decimals: 18 },
  scroll: { name: 'Scroll', symbol: 'ETH', color: '#FFEEDA', decimals: 18 },
  zksync: { name: 'zkSync Era', symbol: 'ETH', color: '#8C8DFC', decimals: 18 },
  solana: { name: 'Solana', symbol: 'SOL', color: '#00D18C', decimals: 9 },
  bitcoin: { name: 'Bitcoin', symbol: 'BTC', color: '#F7931A', decimals: 8 },
  cardano: { name: 'Cardano', symbol: 'ADA', color: '#0033AD', decimals: 6 },
  tron: { name: 'TRON', symbol: 'TRX', color: '#FF060A', decimals: 6 }
};

const transactionTypes = ['Transfer', 'Swap', 'Deposit', 'Withdrawal', 'Stake', 'Unstake', 'Bridge', 'Mint', 'Burn', 'Approve'];

// Utility Functions
const utils = {
  formatAddress: (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  },
  
  formatAmount: (amount, symbol = 'ETH', decimals = 4) => {
    const num = parseFloat(amount);
    return `${num.toFixed(decimals)} ${symbol}`;
  },
  
  formatUSD: (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  },
  
  formatDate: (date) => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(date));
  },
  
  validateAddress: (address, blockchain) => {
    if (!address) return { valid: false, message: 'Address is required' };
    
    // Basic validation patterns
    const patterns = {
      ethereum: /^0x[a-fA-F0-9]{40}$/,
      polygon: /^0x[a-fA-F0-9]{40}$/,
      bsc: /^0x[a-fA-F0-9]{40}$/,
      arbitrum: /^0x[a-fA-F0-9]{40}$/,
      optimism: /^0x[a-fA-F0-9]{40}$/,
      avalanche: /^0x[a-fA-F0-9]{40}$/,
      bitcoin: /^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$/,
      solana: /^[1-9A-HJ-NP-Za-km-z]{32,44}$/,
      cardano: /^addr1[a-z0-9]{98}$/,
      tron: /^T[A-Za-z1-9]{33}$/
    };
    
    const pattern = patterns[blockchain];
    if (!pattern) {
      return { valid: true, message: 'Address format validation not available for this blockchain' };
    }
    
    if (pattern.test(address)) {
      return { valid: true, message: 'Valid address format' };
    } else {
      return { valid: false, message: `Invalid ${blockchains[blockchain]?.name || blockchain} address format` };
    }
  },
  
  generateTransactionHash: () => {
    return '0x' + Array.from({length: 64}, () => Math.floor(Math.random() * 16).toString(16)).join('');
  },
  
  getRandomElement: (array) => {
    return array[Math.floor(Math.random() * array.length)];
  },
  
  addDays: (date, days) => {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
  }
};

// Data Generation Functions
const dataGenerator = {
  generateMockTransactions: (address, blockchain, fromDate, toDate, count = 50) => {
    const transactions = [];
    const startDate = new Date(fromDate);
    const endDate = new Date(toDate);
    const daysDiff = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
    
    const chain = blockchains[blockchain];
    const basePrice = {
      ETH: 2000,
      BTC: 35000,
      MATIC: 0.8,
      BNB: 300,
      AVAX: 25,
      SOL: 80,
      ADA: 0.5,
      TRX: 0.08
    }[chain.symbol] || 100;
    
    for (let i = 0; i < count; i++) {
      const randomDay = Math.floor(Math.random() * daysDiff);
      const txDate = utils.addDays(startDate, randomDay);
      txDate.setHours(Math.floor(Math.random() * 24), Math.floor(Math.random() * 60));
      
      const isIncoming = Math.random() > 0.4;
      const amount = (Math.random() * 10 + 0.001).toFixed(chain.decimals > 8 ? 8 : chain.decimals);
      const usdValue = parseFloat(amount) * basePrice * (0.8 + Math.random() * 0.4);
      
      const transaction = {
        id: i + 1,
        date: txDate.toISOString(),
        hash: utils.generateTransactionHash(),
        type: utils.getRandomElement(transactionTypes),
        direction: isIncoming ? 'in' : 'out',
        from: isIncoming ? utils.generateTransactionHash().slice(0, 42) : address,
        to: isIncoming ? address : utils.generateTransactionHash().slice(0, 42),
        amount: parseFloat(amount),
        token: chain.symbol,
        usdValue: usdValue,
        status: Math.random() > 0.05 ? 'Success' : utils.getRandomElement(['Failed', 'Pending']),
        gasUsed: Math.floor(Math.random() * 100000 + 21000),
        gasPrice: Math.floor(Math.random() * 50 + 10)
      };
      
      transactions.push(transaction);
    }
    
    return transactions.sort((a, b) => new Date(b.date) - new Date(a.date));
  },
  
  calculateSummaryStats: (transactions, blockchain) => {
    const chain = blockchains[blockchain];
    let currentBalance = Math.random() * 100 + 10; // Random starting balance
    let totalVolume = 0;
    let netChange = 0;
    
    transactions.forEach(tx => {
      totalVolume += tx.amount;
      if (tx.direction === 'in') {
        netChange += tx.amount;
      } else {
        netChange -= tx.amount;
      }
    });
    
    const basePrice = {
      ETH: 2000,
      BTC: 35000,
      MATIC: 0.8,
      BNB: 300,
      AVAX: 25,
      SOL: 80,
      ADA: 0.5,
      TRX: 0.08
    }[chain.symbol] || 100;
    
    return {
      currentBalance,
      currentBalanceUSD: currentBalance * basePrice,
      totalTransactions: transactions.length,
      totalVolume,
      totalVolumeUSD: totalVolume * basePrice,
      netChange,
      netChangeUSD: netChange * basePrice,
      netChangePercentage: ((netChange / currentBalance) * 100)
    };
  },
  
  // New method for real blockchain data
  calculateSummaryStatsFromReal: (transactions, blockchain, currentBalance, currentPrice) => {
    const chain = blockchains[blockchain];
    let totalVolume = 0;
    let netChange = 0;
    let totalIncoming = 0;
    let totalOutgoing = 0;
    
    transactions.forEach(tx => {
      const amount = tx.amount || 0;
      totalVolume += amount;
      
      if (tx.direction === 'in') {
        netChange += amount;
        totalIncoming += amount;
      } else if (tx.direction === 'out') {
        netChange -= amount;
        totalOutgoing += amount;
      }
    });
    
    return {
      currentBalance,
      currentBalanceUSD: currentBalance * currentPrice,
      totalTransactions: transactions.length,
      totalVolume,
      totalVolumeUSD: totalVolume * currentPrice,
      netChange,
      netChangeUSD: netChange * currentPrice,
      netChangePercentage: currentBalance > 0 ? ((netChange / currentBalance) * 100) : 0,
      totalIncoming,
      totalOutgoing,
      currentPrice
    };
  },
  
  generateChartData: (transactions, blockchain) => {
    const chain = blockchains[blockchain];
    
    // Balance over time data
    const balanceData = [];
    const volumeData = [];
    const typeData = {};
    
    // Handle empty transactions
    if (!transactions || transactions.length === 0) {
      return {
        balanceData: [],
        volumeData: [],
        typeData: {}
      };
    }
    
    // Group transactions by date
    const transactionsByDate = {};
    transactions.forEach(tx => {
      const date = new Date(tx.date).toDateString();
      if (!transactionsByDate[date]) {
        transactionsByDate[date] = [];
      }
      transactionsByDate[date].push(tx);
      
      // Count transaction types
      if (!typeData[tx.type]) {
        typeData[tx.type] = 0;
      }
      typeData[tx.type]++;
    });
    
    // Generate balance over time
    let runningBalance = Math.random() * 50 + 10;
    const dates = Object.keys(transactionsByDate).sort((a, b) => new Date(a) - new Date(b));
    
    dates.forEach(date => {
      const dayTransactions = transactionsByDate[date];
      let dayVolume = 0;
      let dayChange = 0;
      
      dayTransactions.forEach(tx => {
        dayVolume += tx.amount;
        if (tx.direction === 'in') {
          dayChange += tx.amount;
        } else {
          dayChange -= tx.amount;
        }
      });
      
      runningBalance += dayChange;
      
      balanceData.push({
        x: date,
        y: runningBalance
      });
      
      volumeData.push({
        x: date,
        y: dayVolume
      });
    });
    
    return {
      balanceData,
      volumeData,
      typeData
    };
  }
};

// Chart Functions - Completely rewritten to avoid canvas reuse errors
const chartManager = {
  destroyAllCharts: () => {
    // Destroy all existing charts
    ['balance', 'volume', 'type'].forEach(chartType => {
      if (AppState.charts[chartType]) {
        try {
          AppState.charts[chartType].destroy();
        } catch (e) {
          console.warn(`Error destroying ${chartType} chart:`, e);
        }
        AppState.charts[chartType] = null;
      }
    });
    
    // Also check Chart.js registry and destroy any remaining instances
    ['balance-chart', 'volume-chart', 'type-chart'].forEach(canvasId => {
      const canvas = document.getElementById(canvasId);
      if (canvas) {
        const existingChart = Chart.getChart(canvas);
        if (existingChart) {
          try {
            existingChart.destroy();
          } catch (e) {
            console.warn(`Error destroying chart from canvas ${canvasId}:`, e);
          }
        }
      }
    });
  },
  
  createBalanceChart: (data, blockchain) => {
    const canvas = document.getElementById('balance-chart');
    const chain = blockchains[blockchain];
    
    // Destroy any existing chart on this canvas
    const existingChart = Chart.getChart(canvas);
    if (existingChart) {
      existingChart.destroy();
    }
    
    // Get fresh context
    const ctx = canvas.getContext('2d');
    
    AppState.charts.balance = new Chart(ctx, {
      type: 'line',
      data: {
        datasets: [{
          label: `Balance (${chain.symbol})`,
          data: data.balanceData,
          borderColor: chain.color,
          backgroundColor: chain.color + '20',
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: 'time',
            time: {
              parser: 'yyyy-MM-dd',
              tooltipFormat: 'MMM dd, yyyy',
              displayFormats: {
                day: 'MMM dd'
              }
            }
          },
          y: {
            beginAtZero: false,
            ticks: {
              callback: (value) => value.toFixed(4) + ' ' + chain.symbol
            }
          }
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: (context) => `Balance: ${context.parsed.y.toFixed(4)} ${chain.symbol}`
            }
          }
        }
      }
    });
  },
  
  createVolumeChart: (data, blockchain) => {
    const canvas = document.getElementById('volume-chart');
    const chain = blockchains[blockchain];
    
    // Destroy existing chart instance (check both AppState and Chart.js registry)
    if (AppState.charts.volume) {
      AppState.charts.volume.destroy();
      AppState.charts.volume = null;
    }
    
    // Also check Chart.js internal registry and destroy any existing chart on this canvas
    const existingChart = Chart.getChart(canvas);
    if (existingChart) {
      existingChart.destroy();
    }
    
    // Get fresh context
    const ctx = canvas.getContext('2d');
    
    AppState.charts.volume = new Chart(ctx, {
      type: 'bar',
      data: {
        datasets: [{
          label: `Volume (${chain.symbol})`,
          data: data.volumeData,
          backgroundColor: chain.color + '80',
          borderColor: chain.color,
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: 'time',
            time: {
              parser: 'yyyy-MM-dd',
              tooltipFormat: 'MMM dd, yyyy',
              displayFormats: {
                day: 'MMM dd'
              }
            }
          },
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => value.toFixed(2) + ' ' + chain.symbol
            }
          }
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: (context) => `Volume: ${context.parsed.y.toFixed(4)} ${chain.symbol}`
            }
          }
        }
      }
    });
  },
  
  createTypeChart: (data) => {
    const canvas = document.getElementById('type-chart');
    
    // Destroy existing chart instance (check both AppState and Chart.js registry)
    if (AppState.charts.type) {
      AppState.charts.type.destroy();
      AppState.charts.type = null;
    }
    
    // Also check Chart.js internal registry and destroy any existing chart on this canvas
    const existingChart = Chart.getChart(canvas);
    if (existingChart) {
      existingChart.destroy();
    }
    
    // Get fresh context
    const ctx = canvas.getContext('2d');
    
    const colors = ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5', '#5D878F', '#DB4545', '#D2BA4C', '#964325', '#944454', '#13343B'];
    
    AppState.charts.type = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: Object.keys(data.typeData),
        datasets: [{
          data: Object.values(data.typeData),
          backgroundColor: colors.slice(0, Object.keys(data.typeData).length),
          borderWidth: 2,
          borderColor: '#fff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 20,
              usePointStyle: true
            }
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = ((context.parsed / total) * 100).toFixed(1);
                return `${context.label}: ${context.parsed} (${percentage}%)`;
              }
            }
          }
        }
      }
    });
  }
};

// UI Functions
const ui = {
  showToast: (message, type = 'info') => {
    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    toast.innerHTML = `
      <span>${message}</span>
    `;
    
    document.getElementById('toast-container').appendChild(toast);
    
    setTimeout(() => {
      toast.remove();
    }, 5000);
  },
  
  toggleLoading: (buttonId, isLoading) => {
    const button = document.getElementById(buttonId);
    if (isLoading) {
      button.classList.add('loading');
      button.disabled = true;
    } else {
      button.classList.remove('loading');
      button.disabled = false;
    }
  },
  
  updateSummaryCards: (stats, blockchain) => {
    const chain = blockchains[blockchain];
    
    document.getElementById('current-balance').textContent = utils.formatAmount(stats.currentBalance, chain.symbol);
    document.getElementById('current-balance-usd').textContent = utils.formatUSD(stats.currentBalanceUSD);
    
    document.getElementById('total-transactions').textContent = stats.totalTransactions.toLocaleString();
    
    document.getElementById('total-volume').textContent = utils.formatAmount(stats.totalVolume, chain.symbol);
    document.getElementById('total-volume-usd').textContent = utils.formatUSD(stats.totalVolumeUSD);
    
    const netChangeElement = document.getElementById('net-change');
    const netChangePercentageElement = document.getElementById('net-change-percentage');
    
    const netChangeFormatted = (stats.netChange >= 0 ? '+' : '') + utils.formatAmount(stats.netChange, chain.symbol);
    const netChangePercentageFormatted = (stats.netChangePercentage >= 0 ? '+' : '') + stats.netChangePercentage.toFixed(2) + '%';
    
    netChangeElement.textContent = netChangeFormatted;
    netChangePercentageElement.textContent = netChangePercentageFormatted;
    
    // Update colors based on positive/negative
    if (stats.netChange >= 0) {
      netChangeElement.style.color = 'var(--color-success)';
      netChangePercentageElement.style.color = 'var(--color-success)';
    } else {
      netChangeElement.style.color = 'var(--color-error)';
      netChangePercentageElement.style.color = 'var(--color-error)';
    }
  },
  
  renderTransactionTable: (transactions) => {
    const tbody = document.getElementById('transaction-tbody');
    
    if (transactions.length === 0) {
      tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 2rem;">No transactions found for this address in the selected date range.</td></tr>';
      return;
    }
    
    tbody.innerHTML = transactions.map(tx => {
      const amountClass = tx.direction === 'in' ? 'amount-positive' : 'amount-negative';
      const amountPrefix = tx.direction === 'in' ? '+' : '-';
      const tokenSymbol = tx.tokenSymbol || tx.token || 'Unknown';
      const decimals = tokenSymbol === 'BTC' ? 8 : (tokenSymbol === 'SOL' ? 4 : 6);
      const editedBadge = tx.edited ? ' <span style="font-size: 10px; color: var(--color-warning);">✏️</span>' : '';
      
      return `
        <tr>
          <td>${utils.formatDate(tx.date)}${editedBadge}</td>
          <td><span class="tx-hash" onclick="ui.openTransactionLink('${tx.hash}')" title="${tx.hash}">${utils.formatAddress(tx.hash)}</span></td>
          <td><span class="tx-type">${tx.type}</span></td>
          <td title="${tx.direction === 'in' ? tx.from : tx.to}">${utils.formatAddress(tx.direction === 'in' ? tx.from : tx.to)}</td>
          <td class="${amountClass}">${amountPrefix}${tx.amount.toFixed(decimals)} ${tokenSymbol}</td>
          <td>${tokenSymbol}</td>
          <td>${tx.usdValue ? utils.formatUSD(tx.usdValue) : 'N/A'}</td>
          <td><span class="status status--${tx.status.toLowerCase()}">${tx.status}</span></td>
          <td>
            <div class="transaction-actions">
              <button class="action-btn edit-tx-btn" onclick="balanceEditor.editTransaction('${tx.hash}')" title="Edit">✏️</button>
              <button class="action-btn delete-tx-btn" onclick="balanceEditor.deleteTransaction('${tx.hash}')" title="Delete">🗑</button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  },
  
  updatePagination: () => {
    const totalPages = Math.max(1, Math.ceil(AppState.filteredTransactions.length / AppState.transactionsPerPage));
    const pageInfo = document.getElementById('page-info');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    
    if (AppState.filteredTransactions.length === 0) {
      pageInfo.textContent = 'No transactions';
      prevBtn.disabled = true;
      nextBtn.disabled = true;
    } else {
      pageInfo.textContent = `Page ${AppState.currentPage} of ${totalPages}`;
      prevBtn.disabled = AppState.currentPage === 1;
      nextBtn.disabled = AppState.currentPage === totalPages;
    }
  },
  
  openTransactionLink: (hash) => {
    const blockchain = AppState.currentAnalysis?.blockchain;
    if (!blockchain) {
      ui.showToast('Blockchain information not available', 'error');
      return;
    }
    
    const config = API_CONFIG[blockchain];
    if (!config) {
      ui.showToast('Explorer URL not configured for this blockchain', 'error');
      return;
    }
    
    const explorerUrl = `${config.explorerUrl}/tx/${hash}`;
    window.open(explorerUrl, '_blank');
    ui.showToast(`Opening transaction in block explorer...`, 'info');
  }
};

// Transaction Management
const transactionManager = {
  sortTransactions: (field, direction) => {
    AppState.sortField = field;
    AppState.sortDirection = direction;
    
    AppState.filteredTransactions.sort((a, b) => {
      let aValue = a[field];
      let bValue = b[field];
      
      if (field === 'date') {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      }
      
      if (direction === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
    
    this.renderCurrentPage();
    this.updateSortArrows();
  },
  
  filterTransactions: () => {
    const typeFilter = document.getElementById('type-filter').value;
    const searchFilter = document.getElementById('search-filter').value.toLowerCase();
    
    AppState.filteredTransactions = AppState.transactions.filter(tx => {
      const typeMatch = !typeFilter || tx.type === typeFilter;
      const searchMatch = !searchFilter || 
        tx.hash.toLowerCase().includes(searchFilter) ||
        tx.type.toLowerCase().includes(searchFilter) ||
        tx.from.toLowerCase().includes(searchFilter) ||
        tx.to.toLowerCase().includes(searchFilter);
      
      return typeMatch && searchMatch;
    });
    
    AppState.currentPage = 1;
    this.renderCurrentPage();
    ui.updatePagination();
  },
  
  renderCurrentPage: () => {
    const startIndex = (AppState.currentPage - 1) * AppState.transactionsPerPage;
    const endIndex = startIndex + AppState.transactionsPerPage;
    const pageTransactions = AppState.filteredTransactions.slice(startIndex, endIndex);
    
    ui.renderTransactionTable(pageTransactions);
  },
  
  updateSortArrows: () => {
    document.querySelectorAll('.sortable').forEach(th => {
      th.classList.remove('active');
      const arrow = th.querySelector('.sort-arrow');
      arrow.textContent = '↕';
    });
    
    const activeHeader = document.querySelector(`[data-sort="${AppState.sortField}"]`);
    if (activeHeader) {
      activeHeader.classList.add('active');
      const arrow = activeHeader.querySelector('.sort-arrow');
      arrow.textContent = AppState.sortDirection === 'asc' ? '↑' : '↓';
    }
  },
  
  changePage: (direction) => {
    const totalPages = Math.ceil(AppState.filteredTransactions.length / AppState.transactionsPerPage);
    
    if (direction === 'next' && AppState.currentPage < totalPages) {
      AppState.currentPage++;
    } else if (direction === 'prev' && AppState.currentPage > 1) {
      AppState.currentPage--;
    }
    
    this.renderCurrentPage();
    ui.updatePagination();
  }
};

// Manual Balance Editor Manager
const balanceEditor = {
  isVisible: false,
  originalData: null,
  manualEdits: {
    openingBalance: null,
    currentBalance: null,
    deletedTransactions: new Set()
  },

  toggleEditor: () => {
    const editor = document.getElementById('balance-editor');
    const toggleBtn = document.getElementById('toggle-balance-editor-btn');
    
    balanceEditor.isVisible = !balanceEditor.isVisible;
    editor.style.display = balanceEditor.isVisible ? 'block' : 'none';
    toggleBtn.textContent = balanceEditor.isVisible ? '✖ Close Editor' : '✏️ Edit Balances';
    
    if (balanceEditor.isVisible && !balanceEditor.originalData) {
      balanceEditor.loadCurrentData();
    }
  },

  loadCurrentData: () => {
    if (!AppState.currentAnalysis) return;
    
    const { stats } = AppState.currentAnalysis;
    
    // Store original data for reset
    balanceEditor.originalData = {
      openingBalance: {
        native: stats.currentBalance || 0, // This should be actual opening balance
        tokens: []
      },
      currentBalance: {
        native: stats.currentBalance || 0,
        tokens: []
      }
    };
    
    // Populate fields
    document.getElementById('edit-opening-native').value = balanceEditor.originalData.openingBalance.native;
    document.getElementById('edit-current-native').value = balanceEditor.originalData.currentBalance.native;
  },

  addTokenField: (section) => {
    const container = document.getElementById(`${section}-tokens-editor`);
    const tokenItem = document.createElement('div');
    tokenItem.className = 'token-editor-item';
    tokenItem.innerHTML = `
      <input type="text" placeholder="Token Symbol" class="token-symbol">
      <input type="number" step="any" placeholder="Amount" class="token-amount">
      <button class="remove-token-btn" onclick="this.parentElement.remove()">🗑</button>
    `;
    container.appendChild(tokenItem);
  },

  applyChanges: () => {
    // Get edited values
    const openingNative = parseFloat(document.getElementById('edit-opening-native').value) || 0;
    const currentNative = parseFloat(document.getElementById('edit-current-native').value) || 0;
    
    // Get opening tokens
    const openingTokens = [];
    document.querySelectorAll('#opening-tokens-editor .token-editor-item').forEach(item => {
      const symbol = item.querySelector('.token-symbol').value.trim();
      const amount = parseFloat(item.querySelector('.token-amount').value) || 0;
      if (symbol && amount > 0) {
        openingTokens.push({ symbol, amount });
      }
    });
    
    // Get current tokens
    const currentTokens = [];
    document.querySelectorAll('#current-tokens-editor .token-editor-item').forEach(item => {
      const symbol = item.querySelector('.token-symbol').value.trim();
      const amount = parseFloat(item.querySelector('.token-amount').value) || 0;
      if (symbol && amount > 0) {
        currentTokens.push({ symbol, amount });
      }
    });
    
    // Store manual edits
    balanceEditor.manualEdits.openingBalance = {
      native: openingNative,
      tokens: openingTokens
    };
    
    balanceEditor.manualEdits.currentBalance = {
      native: currentNative,
      tokens: currentTokens
    };
    
    ui.showToast('✅ Balance changes applied! These values will be used in exports.', 'success');
  },

  resetChanges: () => {
    if (!balanceEditor.originalData) return;
    
    // Reset to original values
    document.getElementById('edit-opening-native').value = balanceEditor.originalData.openingBalance.native;
    document.getElementById('edit-current-native').value = balanceEditor.originalData.currentBalance.native;
    
    // Clear token fields
    document.getElementById('opening-tokens-editor').innerHTML = '';
    document.getElementById('current-tokens-editor').innerHTML = '';
    
    // Clear manual edits
    balanceEditor.manualEdits = {
      openingBalance: null,
      currentBalance: null,
      deletedTransactions: new Set()
    };
    
    ui.showToast('Reset to original values', 'info');
  },

  deleteTransaction: (txHash) => {
    if (confirm('Are you sure you want to delete this transaction?')) {
      balanceEditor.manualEdits.deletedTransactions.add(txHash);
      
      // Remove from filtered transactions
      AppState.filteredTransactions = AppState.filteredTransactions.filter(tx => tx.hash !== txHash);
      
      // Re-render table
      transactionManager.renderTransactions();
      transactionManager.updatePagination();
      
      ui.showToast('Transaction deleted. It will be excluded from exports.', 'success');
    }
  },

  editTransaction: (txHash) => {
    const tx = AppState.filteredTransactions.find(t => t.hash === txHash);
    if (!tx) return;
    
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h3>Edit Transaction</h3>
          <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Date</label>
            <input type="text" id="edit-tx-date" value="${tx.date}">
          </div>
          <div class="form-group">
            <label>Type</label>
            <select id="edit-tx-type">
              ${transactionTypes.map(type => 
                `<option value="${type}" ${tx.type === type ? 'selected' : ''}>${type}</option>`
              ).join('')}
            </select>
          </div>
          <div class="form-group">
            <label>From/To</label>
            <input type="text" id="edit-tx-from" value="${tx.from || ''}">
          </div>
          <div class="form-group">
            <label>Amount</label>
            <input type="number" step="any" id="edit-tx-amount" value="${tx.amount}">
          </div>
          <div class="form-group">
            <label>Token</label>
            <input type="text" id="edit-tx-token" value="${tx.token}">
          </div>
          <div class="form-group">
            <label>USD Value</label>
            <input type="number" step="any" id="edit-tx-usd" value="${tx.usd || 0}">
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-cancel" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
          <button class="modal-save" id="save-tx-edit">Save Changes</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Save handler
    document.getElementById('save-tx-edit').addEventListener('click', () => {
      tx.date = document.getElementById('edit-tx-date').value;
      tx.type = document.getElementById('edit-tx-type').value;
      tx.from = document.getElementById('edit-tx-from').value;
      tx.amount = parseFloat(document.getElementById('edit-tx-amount').value) || 0;
      tx.token = document.getElementById('edit-tx-token').value;
      tx.usd = parseFloat(document.getElementById('edit-tx-usd').value) || 0;
      tx.edited = true; // Mark as edited
      
      transactionManager.renderTransactions();
      modal.remove();
      ui.showToast('Transaction updated successfully', 'success');
    });
  },

  getEditedData: () => {
    return {
      openingBalance: balanceEditor.manualEdits.openingBalance,
      currentBalance: balanceEditor.manualEdits.currentBalance,
      transactions: AppState.filteredTransactions.filter(tx => 
        !balanceEditor.manualEdits.deletedTransactions.has(tx.hash)
      )
    };
  }
};

// Export Manager
const exportManager = {
  exportToPDF: async () => {
    ui.toggleLoading('export-pdf-btn', true);
    
    try {
      if (!AppState.currentAnalysis) {
        throw new Error('No analysis data available to export');
      }
      
      const { address, blockchain, fromDate, toDate } = AppState.currentAnalysis;
      
      // Get manual edits if any
      const manualData = balanceEditor.getEditedData();
      
      ui.showToast('Generating PDF with USD and AED conversions...', 'info');
      
      // Call backend to generate PDF
      await apiService.exportPDF(blockchain, address, fromDate, toDate, manualData);
      
      ui.showToast('✅ PDF report with USD/AED conversions downloaded successfully!', 'success');
      
    } catch (error) {
      console.error('PDF export error:', error);
      ui.showToast(`Failed to generate PDF: ${error.message}`, 'error');
    } finally {
      ui.toggleLoading('export-pdf-btn', false);
    }
  },
  
  exportToPDFOld: async () => {
    // Old client-side PDF generation (kept as backup)
    ui.toggleLoading('export-pdf-btn', true);
    
    try {
      if (!AppState.currentAnalysis) {
        throw new Error('No analysis data available to export');
      }
      
      const { jsPDF } = window.jspdf;
      const doc = new jsPDF();
      
      const chain = blockchains[AppState.currentAnalysis.blockchain];
      
      // Add title
      doc.setFontSize(20);
      doc.setTextColor(40, 40, 40);
      doc.text('Blockchain Account Statement', 20, 20);
      
      // Add analysis details
      doc.setFontSize(11);
      doc.setTextColor(80, 80, 80);
      doc.text(`Network: ${chain.name}`, 20, 35);
      doc.text(`Address: ${AppState.currentAnalysis.address}`, 20, 42);
      doc.text(`Period: ${AppState.currentAnalysis.fromDate} to ${AppState.currentAnalysis.toDate}`, 20, 49);
      doc.text(`Generated: ${new Date().toLocaleString()}`, 20, 56);
      doc.text(`Total Transactions: ${AppState.transactions.length}`, 20, 63);
      
      // Add line separator
      doc.setDrawColor(200, 200, 200);
      doc.line(20, 68, 190, 68);
      
      // Add summary stats
      const stats = AppState.currentAnalysis.stats;
      doc.setFontSize(14);
      doc.setTextColor(40, 40, 40);
      doc.text('Account Summary:', 20, 78);
      
      doc.setFontSize(10);
      doc.setTextColor(60, 60, 60);
      doc.text(`Current Balance: ${utils.formatAmount(stats.currentBalance, chain.symbol)} (${utils.formatUSD(stats.currentBalanceUSD)})`, 30, 88);
      doc.text(`Total Volume: ${utils.formatAmount(stats.totalVolume, chain.symbol)} (${utils.formatUSD(stats.totalVolumeUSD)})`, 30, 95);
      doc.text(`Net Change: ${stats.netChange >= 0 ? '+' : ''}${utils.formatAmount(stats.netChange, chain.symbol)} (${stats.netChangePercentage.toFixed(2)}%)`, 30, 102);
      
      if (stats.currentPrice) {
        doc.text(`Current Price: ${utils.formatUSD(stats.currentPrice)} per ${chain.symbol}`, 30, 109);
      }
      
      // Add transaction list
      doc.setFontSize(14);
      doc.setTextColor(40, 40, 40);
      doc.text('Recent Transactions:', 20, 122);
      
      let yPos = 132;
      const maxTransactions = 30; // Limit to prevent PDF size issues
      
      AppState.transactions.slice(0, maxTransactions).forEach((tx, index) => {
        if (yPos > 270) {
          doc.addPage();
          yPos = 20;
        }
        
        doc.setFontSize(8);
        doc.setTextColor(50, 50, 50);
        
        const date = utils.formatDate(tx.date);
        const type = tx.type;
        const amount = `${tx.direction === 'in' ? '+' : '-'}${tx.amount.toFixed(6)} ${tx.tokenSymbol || tx.token}`;
        const status = tx.status;
        
        doc.text(`${date} | ${type} | ${amount} | ${status}`, 25, yPos);
        yPos += 7;
      });
      
      if (AppState.transactions.length > maxTransactions) {
        doc.setFontSize(8);
        doc.setTextColor(100, 100, 100);
        doc.text(`... and ${AppState.transactions.length - maxTransactions} more transactions`, 25, yPos);
      }
      
      // Add footer
      const pageCount = doc.internal.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(150, 150, 150);
        doc.text(`Page ${i} of ${pageCount} | Blockchain Balance Screener`, 20, 285);
      }
      
      const filename = `${chain.name}_${AppState.currentAnalysis.address.slice(0, 10)}_statement.pdf`;
      doc.save(filename);
      
      ui.showToast('✅ PDF report downloaded successfully!', 'success');
      
    } catch (error) {
      console.error('PDF export error:', error);
      ui.showToast(`Failed to generate PDF: ${error.message}`, 'error');
    } finally {
      ui.toggleLoading('export-pdf-btn', false);
    }
  },
  
  exportToCSV: async () => {
    ui.toggleLoading('export-csv-btn', true);
    
    try {
      if (!AppState.currentAnalysis) {
        throw new Error('No analysis data available to export');
      }
      
      const { address, blockchain, fromDate, toDate } = AppState.currentAnalysis;
      
      // Get manual edits if any
      const manualData = balanceEditor.getEditedData();
      
      ui.showToast('Generating CSV with opening balance...', 'info');
      
      // Call backend to generate CSV with opening balance
      await apiService.exportCSV(blockchain, address, fromDate, toDate, manualData);
      
      ui.showToast('✅ CSV report with opening balance downloaded successfully!', 'success');
      
    } catch (error) {
      console.error('CSV export error:', error);
      ui.showToast(`Failed to generate CSV: ${error.message}`, 'error');
    } finally {
      ui.toggleLoading('export-csv-btn', false);
    }
  }
};

// Main Analysis Function - Now using Python Backend
const performAnalysis = async (formData) => {
  const { address, blockchain, fromDate, toDate } = formData;
  
  ui.toggleLoading('analyze-btn', true);
  ui.showToast(`Fetching real data from ${blockchains[blockchain].name} blockchain...`, 'info');
  
  try {
    // Call Python backend for complete analysis
    const analysisData = await apiService.analyzeAddress(blockchain, address, fromDate, toDate);
    
    const transactions = analysisData.transactions || [];
    const balance = parseFloat(analysisData.balance || 0);
    const chain = blockchains[blockchain];
    
    // Convert balance from wei/satoshi to main unit
    let currentBalance = balance;
    if (blockchain === 'bitcoin') {
      currentBalance = balance / 1e8; // Satoshis to BTC
    } else if (chain.decimals === 18) {
      currentBalance = balance / 1e18; // Wei to ETH/MATIC/etc
    } else {
      currentBalance = balance / Math.pow(10, chain.decimals);
    }
    
    if (transactions.length === 0) {
      ui.showToast('No transactions found in the selected date range. This might be a new address or no activity during this period.', 'warning');
    } else {
      ui.showToast(`Found ${transactions.length} transactions!`, 'success');
    }
    
    // Calculate statistics from real data
    const totalIn = analysisData.statistics?.total_in || 0;
    const totalOut = analysisData.statistics?.total_out || 0;
    const netChange = totalIn - totalOut;
    const netChangePercentage = currentBalance > 0 ? ((netChange / currentBalance) * 100) : 0;
    
    const stats = {
      totalTransactions: transactions.length,
      totalIn: totalIn,
      totalOut: totalOut,
      netChange: netChange,
      netChangePercentage: netChangePercentage,
      currentBalance: currentBalance,
      averageTransaction: transactions.length > 0 ? 
        (totalIn + totalOut) / transactions.length : 0,
      largestTransaction: transactions.length > 0 ? 
        Math.max(...transactions.map(tx => tx.amount)) : 0,
      totalUSD: 0, // Will be calculated with price data
      averageValue: transactions.length > 0 ? 
        (totalIn + totalOut) / (2 * transactions.length) : 0
    };
    
    // Update application state
    AppState.currentAnalysis = { address, blockchain, fromDate, toDate, stats };
    AppState.transactions = transactions;
    AppState.filteredTransactions = [...transactions];
    AppState.currentPage = 1;
    
    // Update UI
    ui.updateSummaryCards(stats, blockchain);
    document.getElementById('date-range-display').textContent = `${fromDate} to ${toDate}`;
    
    // Destroy all existing charts first
    chartManager.destroyAllCharts();
    
    // Only create charts if we have transactions
    if (transactions.length > 0) {
      const chartsSection = document.querySelector('.charts-section');
      if (chartsSection) {
        chartsSection.style.display = 'block';
      }
      
      const chartData = dataGenerator.generateChartData(transactions, blockchain);
      chartManager.createBalanceChart(chartData, blockchain);
      chartManager.createVolumeChart(chartData, blockchain);
      chartManager.createTypeChart(chartData);
    } else {
      // Hide charts section if no transactions
      const chartsSection = document.querySelector('.charts-section');
      if (chartsSection) {
        chartsSection.style.display = 'none';
      }
    }
    
    // Render transactions
    transactionManager.renderCurrentPage();
    ui.updatePagination();
    
    // Show results
    document.getElementById('results-dashboard').style.display = 'block';
    
    // Scroll to results
    document.getElementById('results-dashboard').scrollIntoView({ behavior: 'smooth' });
    
    if (transactions.length > 0) {
      ui.showToast(`✅ Analysis completed! Found ${transactions.length} transactions.`, 'success');
    } else {
      ui.showToast(`ℹ️ Analysis completed. No transactions found in the selected date range.`, 'info');
    }
    
  } catch (error) {
    console.error('Analysis error:', error);
    ui.showToast(`Failed to fetch blockchain data: ${error.message}`, 'error');
  } finally {
    ui.toggleLoading('analyze-btn', false);
  }
};

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
  // Set default date range (last 30 days)
  const toDate = new Date();
  const fromDate = new Date();
  fromDate.setDate(fromDate.getDate() - 30);
  
  document.getElementById('from-date').value = fromDate.toISOString().split('T')[0];
  document.getElementById('to-date').value = toDate.toISOString().split('T')[0];
  
  // Form submission
  document.getElementById('analysis-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
      address: document.getElementById('address').value.trim(),
      blockchain: document.getElementById('blockchain').value,
      fromDate: document.getElementById('from-date').value,
      toDate: document.getElementById('to-date').value
    };
    
    // Validation
    if (!formData.address || !formData.blockchain || !formData.fromDate || !formData.toDate) {
      ui.showToast('Please fill in all required fields', 'error');
      return;
    }
    
    const addressValidation = utils.validateAddress(formData.address, formData.blockchain);
    if (!addressValidation.valid) {
      ui.showToast(addressValidation.message, 'error');
      return;
    }
    
    if (new Date(formData.fromDate) >= new Date(formData.toDate)) {
      ui.showToast('From date must be before to date', 'error');
      return;
    }
    
    await performAnalysis(formData);
  });
  
  // Reset form
  document.getElementById('reset-btn').addEventListener('click', () => {
    document.getElementById('analysis-form').reset();
    document.getElementById('address-validation').textContent = '';
    document.getElementById('results-dashboard').style.display = 'none';
    ui.showToast('Form reset successfully', 'info');
  });
  
  // Address validation
  document.getElementById('address').addEventListener('input', (e) => {
    const address = e.target.value.trim();
    const blockchain = document.getElementById('blockchain').value;
    const validationElement = document.getElementById('address-validation');
    
    if (address && blockchain) {
      const validation = utils.validateAddress(address, blockchain);
      validationElement.textContent = validation.message;
      validationElement.className = validation.valid ? 'address-validation valid' : 'address-validation invalid';
    } else {
      validationElement.textContent = '';
      validationElement.className = 'address-validation';
    }
  });
  
  // Blockchain selection change
  document.getElementById('blockchain').addEventListener('change', () => {
    const addressInput = document.getElementById('address');
    if (addressInput.value.trim()) {
      addressInput.dispatchEvent(new Event('input'));
    }
  });
  
  // Sample address buttons
  document.querySelectorAll('.sample-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const address = e.target.dataset.address;
      const chain = e.target.dataset.chain;
      
      document.getElementById('address').value = address;
      document.getElementById('blockchain').value = chain;
      
      // Trigger validation
      document.getElementById('address').dispatchEvent(new Event('input'));
    });
  });
  
  // Transaction sorting
  document.querySelectorAll('.sortable').forEach(th => {
    th.addEventListener('click', () => {
      const field = th.dataset.sort;
      const currentDirection = AppState.sortField === field ? AppState.sortDirection : 'desc';
      const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
      
      transactionManager.sortTransactions(field, newDirection);
    });
  });
  
  // Transaction filtering
  document.getElementById('type-filter').addEventListener('change', transactionManager.filterTransactions);
  document.getElementById('search-filter').addEventListener('input', transactionManager.filterTransactions);
  
  // Pagination
  document.getElementById('prev-btn').addEventListener('click', () => transactionManager.changePage('prev'));
  document.getElementById('next-btn').addEventListener('click', () => transactionManager.changePage('next'));
  
  // Export buttons (transaction section)
  document.getElementById('export-pdf-btn').addEventListener('click', exportManager.exportToPDF);
  document.getElementById('export-csv-btn').addEventListener('click', exportManager.exportToCSV);
  
  // Export buttons (export section - alternate IDs)
  const pdfBtnAlt = document.getElementById('export-pdf-btn-alt');
  const csvBtnAlt = document.getElementById('export-csv-btn-alt');
  if (pdfBtnAlt) pdfBtnAlt.addEventListener('click', exportManager.exportToPDF);
  if (csvBtnAlt) csvBtnAlt.addEventListener('click', exportManager.exportToCSV);
  
  // Balance editor buttons
  const toggleEditorBtn = document.getElementById('toggle-balance-editor-btn');
  const applyEditsBtn = document.getElementById('apply-balance-edits-btn');
  const resetEditsBtn = document.getElementById('reset-balance-edits-btn');
  const addOpeningTokenBtn = document.getElementById('add-opening-token-btn');
  const addCurrentTokenBtn = document.getElementById('add-current-token-btn');
  
  if (toggleEditorBtn) toggleEditorBtn.addEventListener('click', balanceEditor.toggleEditor);
  if (applyEditsBtn) applyEditsBtn.addEventListener('click', balanceEditor.applyChanges);
  if (resetEditsBtn) resetEditsBtn.addEventListener('click', balanceEditor.resetChanges);
  if (addOpeningTokenBtn) addOpeningTokenBtn.addEventListener('click', () => balanceEditor.addTokenField('opening'));
  if (addCurrentTokenBtn) addCurrentTokenBtn.addEventListener('click', () => balanceEditor.addTokenField('current'));
});

// Global error handler
window.addEventListener('error', (e) => {
  console.error('Global error:', e.error);
  ui.showToast('An unexpected error occurred', 'error');
});

// Export for potential external use
window.BlockchainBalanceScreener = {
  AppState,
  utils,
  dataGenerator,
  chartManager,
  ui,
  transactionManager,
  exportManager,
  balanceEditor
};