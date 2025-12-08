import { useState, useEffect } from 'react'
import { getCards, createCard, uploadStatement, getReport, getTransactions } from './lib/api'
import { Upload, CreditCard, PieChart as PieIcon, Plus, ArrowLeft, Lock, FileText, ChevronRight, List } from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import clsx from 'clsx'
import './index.css';

function App() {
  const [cards, setCards] = useState([])
  const [selectedCard, setSelectedCard] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [newCardName, setNewCardName] = useState('')
  const [newCardLast4, setNewCardLast4] = useState('')
  const [newCardBank, setNewCardBank] = useState('other')

  useEffect(() => {
    fetchCards()
  }, [])

  const fetchCards = async () => {
    try {
      const { data } = await getCards()
      setCards(data)
    } catch (error) {
      console.error("Failed to fetch cards", error)
    }
  }

  const handleCreateCard = async (e) => {
    e.preventDefault()
    try {
      await createCard({
        name: newCardName,
        last_4_digits: newCardLast4,
        bank: newCardBank
      })
      setIsModalOpen(false)
      fetchCards()
      setNewCardName('')
      setNewCardLast4('')
      setNewCardBank('other')
    } catch (error) {
      console.error("Failed to create card", error)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between sticky top-0 z-10">
        <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
          Credit Card Wrapped
        </h1>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 bg-slate-900 text-white px-4 py-2 rounded-lg hover:bg-slate-800 transition-colors text-sm font-medium"
        >
          <Plus size={16} />
          Add Card
        </button>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {cards.length === 0 ? (
          <div className="text-center py-20">
            <div className="bg-purple-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <CreditCard className="text-purple-600" size={32} />
            </div>
            <h2 className="text-2xl font-semibold mb-2">No cards added yet</h2>
            <p className="text-slate-500 mb-6">Add a credit card to get started with your wrapped report.</p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-6 py-2.5 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors"
            >
              Add First Card
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Sidebar / Card List */}
            <div className="md:col-span-1 space-y-4">
              <h3 className="text-sm uppercase tracking-wider text-slate-500 font-semibold mb-2">My Cards</h3>
              <div className="space-y-2">
                {cards.map(card => (
                  <div
                    key={card.id}
                    onClick={() => setSelectedCard(card)}
                    className={clsx(
                      "p-4 rounded-xl cursor-pointer border transition-all duration-200",
                      selectedCard?.id === card.id
                        ? "bg-white border-purple-500 shadow-md ring-1 ring-purple-100"
                        : "bg-white border-slate-200 hover:border-purple-300 hover:shadow-sm"
                    )}
                  >
                    <div className="font-semibold">{card.name}</div>
                    <div className="text-slate-500 text-sm mt-1">•••• {card.last_4_digits}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Main Content Area */}
            <div className="md:col-span-3">
              {selectedCard ? (
                <CardDetails card={selectedCard} />
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-2xl p-12">
                  <PieChart size={48} className="mb-4 opacity-50" />
                  <p>Select a card to view insights</p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Add Card Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-2xl transform transition-all">
            <h2 className="text-xl font-bold mb-4">Add New Card</h2>
            <form onSubmit={handleCreateCard} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Card Name</label>
                <input
                  type="text"
                  value={newCardName}
                  onChange={e => setNewCardName(e.target.value)}
                  placeholder="e.g. HDFC Regalia"
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Last 4 Digits</label>
                <input
                  type="text"
                  value={newCardLast4}
                  onChange={e => setNewCardLast4(e.target.value)}
                  placeholder="1234"
                  maxLength={4}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Bank</label>
                <select
                  value={newCardBank}
                  onChange={e => setNewCardBank(e.target.value)}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none bg-white"
                >
                  <option value="hdfc">HDFC Bank</option>
                  <option value="axis">Axis Bank</option>
                  <option value="other">Other</option>
                </select>
                <p className="text-xs text-slate-500 mt-1">
                  Select your bank for optimized statement parsing
                </p>
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="flex-1 px-4 py-2 border border-slate-300 rounded-lg text-slate-700 font-medium hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-slate-900 text-white rounded-lg font-medium hover:bg-slate-800"
                >
                  Save Card
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

// Sub-component for details
function CardDetails({ card }) {
  const [view, setView] = useState('menu') // menu, upload, report

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 min-h-[500px]">
        <div className="flex items-center gap-4 mb-6">
          {view !== 'menu' && (
            <button onClick={() => setView('menu')} className="p-2 hover:bg-slate-100 rounded-full transition-colors">
              <ArrowLeft size={20} />
            </button>
          )}
          <div>
            <h2 className="text-2xl font-bold">{card.name}</h2>
            <p className="text-slate-500 text-sm">•••• {card.last_4_digits}</p>
          </div>
        </div>

        {view === 'menu' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div
              onClick={() => setView('upload')}
              className="bg-slate-50 p-6 rounded-2xl border border-slate-200 hover:border-purple-200 hover:scale-[1.02] transition-all cursor-pointer group flex flex-col items-center text-center justify-center gap-3 h-48"
            >
              <div className="bg-white p-3 rounded-full shadow-sm text-purple-600 group-hover:text-purple-700">
                <Upload size={32} />
              </div>
              <div>
                <span className="font-semibold text-lg block mb-1">Upload Statement</span>
                <p className="text-sm text-slate-500">Add PDF statements to analyze</p>
              </div>
            </div>

            <div
              onClick={() => setView('transactions')}
              className="bg-slate-50 p-6 rounded-2xl border border-slate-200 hover:border-purple-200 hover:scale-[1.02] transition-all cursor-pointer group flex flex-col items-center text-center justify-center gap-3 h-48"
            >
              <div className="bg-white p-3 rounded-full shadow-sm text-purple-600 group-hover:text-purple-700">
                <List size={32} />
              </div>
              <div>
                <span className="font-semibold text-lg block mb-1">View Transactions</span>
                <p className="text-sm text-slate-500">See all extracted transactions</p>
              </div>
            </div>

            <div
              onClick={() => setView('report')}
              className="bg-slate-50 p-6 rounded-2xl border border-slate-200 hover:border-purple-200 hover:scale-[1.02] transition-all cursor-pointer group flex flex-col items-center text-center justify-center gap-3 h-48"
            >
              <div className="bg-white p-3 rounded-full shadow-sm text-purple-600 group-hover:text-purple-700">
                <PieIcon size={32} />
              </div>
              <div>
                <span className="font-semibold text-lg block mb-1">Your Wrapped Report</span>
                <p className="text-sm text-slate-500">Uncover your spending habits</p>
              </div>
            </div>
          </div>
        )}

        {view === 'upload' && <UploadView card={card} onComplete={() => setView('report')} />}
        {view === 'transactions' && <TransactionsView card={card} />}
        {view === 'report' && <ReportView card={card} />}
      </div>
    </div>
  )
}

function UploadView({ card, onComplete }) {
  const [files, setFiles] = useState([])
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState(null) // null, error, success

  const handleUpload = async (e) => {
    e.preventDefault()
    if (files.length === 0) return

    setLoading(true)
    setStatus(null)
    try {
      await uploadStatement(card.id, files, password)
      setStatus('success')
      setTimeout(() => onComplete(), 1500)
    } catch (error) {
      console.error(error)
      setStatus('error')
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files)
    setFiles(selectedFiles)
  }

  return (
    <div className="max-w-md mx-auto">
      <h3 className="text-xl font-semibold mb-6 text-center">Upload PDF Statements</h3>
      <form onSubmit={handleUpload} className="space-y-4">
        <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center hover:border-purple-400 transition-colors bg-slate-50/50">
          <input
            type="file"
            accept=".pdf"
            multiple
            onChange={handleFileChange}
            className="hidden"
            id="file-upload"
          />
          <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center gap-2">
            <FileText className="text-slate-400" size={40} />
            <span className="text-slate-700 font-medium">
              {files.length > 0 ? `${files.length} file(s) selected` : "Click to select PDFs"}
            </span>
            <span className="text-xs text-slate-500">You can select multiple files</span>
          </label>
          {files.length > 0 && (
            <div className="mt-4 text-left">
              <p className="text-xs font-medium text-slate-600 mb-2">Selected files:</p>
              <ul className="text-xs text-slate-500 space-y-1">
                {files.map((file, idx) => (
                  <li key={idx} className="truncate">• {file.name}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Password (Optional)
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-2.5 text-slate-400" size={16} />
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Statement password if any"
              className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
            />
          </div>
          <p className="text-xs text-slate-500 mt-1">
            e.g. First 4 letters of name + DDMM
          </p>
        </div>

        {status === 'error' && (
          <div className="p-3 bg-red-50 text-red-600 rounded-lg text-sm text-center">
            Failed to process. Check password/format.
          </div>
        )}
        {status === 'success' && (
          <div className="p-3 bg-green-50 text-green-600 rounded-lg text-sm text-center">
            Processing complete! Redirecting...
          </div>
        )}

        <button
          type="submit"
          disabled={files.length === 0 || loading}
          className="w-full bg-slate-900 text-white py-2.5 rounded-lg disabled:opacity-50 hover:bg-slate-800 transition-colors font-medium flex items-center justify-center gap-2"
        >
          {loading ? (
            <span className="animate-pulse">Processing...</span>
          ) : (
            <>
              Upload & Process <ChevronRight size={16} />
            </>
          )}
        </button>
      </form>
    </div>
  )
}

function TransactionsView({ card }) {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        console.log('Fetching transactions for card:', card.id)
        const res = await getTransactions(card.id)
        console.log('API Response:', res)
        console.log('Transactions data:', res.data)
        setTransactions(res.data || [])
      } catch (error) {
        console.error('Error fetching transactions:', error)
        setError(error.message)
      } finally {
        setLoading(false)
      }
    }
    fetchTransactions()
  }, [card.id])

  if (loading) return <div className="text-center py-20 text-slate-400">Loading transactions...</div>
  if (error) return (
    <div className="text-center py-20">
      <h3 className="text-lg font-medium text-red-700">Error loading transactions</h3>
      <p className="text-slate-500">{error}</p>
    </div>
  )
  if (!transactions || transactions.length === 0) return (
    <div className="text-center py-20">
      <h3 className="text-lg font-medium text-slate-700">No transactions found</h3>
      <p className="text-slate-500">Upload a statement to see transactions.</p>
    </div>
  )

  return (
    <div className="overflow-x-auto">
      <h3 className="text-xl font-semibold mb-4">All Transactions ({transactions.length})</h3>
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Date</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Description</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Category</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Type</th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-slate-600 uppercase tracking-wider">Amount</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {transactions.map((txn, idx) => (
              <tr key={idx} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 text-sm text-slate-600 whitespace-nowrap">
                  {new Date(txn.date).toLocaleDateString('en-IN')}
                </td>
                <td className="px-4 py-3 text-sm text-slate-900 max-w-md truncate" title={txn.description}>
                  {txn.description}
                </td>
                <td className="px-4 py-3 text-sm">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                    {txn.category}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm">
                  {txn.is_credit ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Credit
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      Debit
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 text-sm font-semibold text-slate-900 text-right whitespace-nowrap">
                  ₹{txn.amount.toLocaleString('en-IN')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

const COLORS = ['#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#6366f1', '#64748b'];

function ReportView({ card }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const res = await getReport(card.id)
        setData(res.data)
      } catch (error) {
        console.error(error)
      } finally {
        setLoading(false)
      }
    }
    fetchReport()
  }, [card.id])

  if (loading) return <div className="text-center py-20 text-slate-400">Loading insights...</div>
  if (!data || data.transaction_count === 0) return (
    <div className="text-center py-20">
      <h3 className="text-lg font-medium text-slate-700">No transactions found</h3>
      <p className="text-slate-500">Upload a statement to see your wrapped report.</p>
    </div>
  )

  const chartData = Object.entries(data.category_spend).map(([name, value]) => ({ name, value }))

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-gradient-to-br from-purple-500 to-indigo-600 p-6 rounded-2xl text-white shadow-lg">
          <p className="text-purple-100 text-sm font-medium uppercase tracking-wide">Total Spend</p>
          <h3 className="text-3xl font-bold mt-1">₹{data.total_spend.toLocaleString('en-IN')}</h3>
          <p className="text-xs text-purple-200 mt-2 opacity-80">{data.transaction_count} transactions</p>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-emerald-600 p-6 rounded-2xl text-white shadow-lg">
          <p className="text-green-100 text-sm font-medium uppercase tracking-wide">Total Cashback</p>
          <h3 className="text-3xl font-bold mt-1">₹{data.total_cashback.toLocaleString('en-IN')}</h3>
          <p className="text-xs text-green-200 mt-2 opacity-80">{data.cashback_count} cashback</p>
        </div>

        <div className="bg-gradient-to-br from-red-500 to-rose-600 p-6 rounded-2xl text-white shadow-lg">
          <p className="text-red-100 text-sm font-medium uppercase tracking-wide">Hidden Charges</p>
          <h3 className="text-3xl font-bold mt-1">₹{data.total_hidden_charges.toLocaleString('en-IN')}</h3>
          <p className="text-xs text-red-200 mt-2 opacity-80">{data.hidden_charge_count} charges</p>
        </div>

        <div className="bg-white border border-slate-100 p-6 rounded-2xl shadow-sm">
          <p className="text-slate-500 text-sm font-medium uppercase tracking-wide">Net Spend</p>
          <h3 className="text-3xl font-bold mt-1 text-slate-900">₹{data.net_spend.toLocaleString('en-IN')}</h3>
          <p className="text-xs text-slate-400 mt-2">After cashback</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white border border-slate-100 p-6 rounded-2xl shadow-sm">
          <p className="text-slate-500 text-sm font-medium uppercase tracking-wide">Biggest Purchase</p>
          {data.largest_transaction ? (
            <>
              <h3 className="text-xl font-bold mt-1 truncate" title={data.largest_transaction.description}>
                {data.largest_transaction.description}
              </h3>
              <p className="text-2xl text-slate-900 font-semibold mt-1">₹{data.largest_transaction.amount.toLocaleString('en-IN')}</p>
              <p className="text-xs text-slate-400 mt-1">{new Date(data.largest_transaction.date).toLocaleDateString()}</p>
            </>
          ) : (
            <p>N/A</p>
          )}
        </div>
        <div className="bg-white border border-slate-100 p-6 rounded-2xl shadow-sm flex flex-col justify-center">
          <p className="text-slate-500 text-sm font-medium uppercase tracking-wide mb-2">Most Frequent Category</p>
          {chartData.length > 0 && (
            <h3 className="text-xl font-bold text-slate-800">
              {chartData.sort((a, b) => b.value - a.value)[0].name}
            </h3>
          )}
        </div>
      </div>

      <div className="bg-slate-50 rounded-2xl p-6 border border-slate-100">
        <h3 className="text-lg font-semibold mb-6">Spending by Category</h3>
        <div className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                fill="#8884d8"
                paddingAngle={5}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `₹${value.toLocaleString('en-IN')}`} />
              <Legend verticalAlign="bottom" height={36} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}

export default App
