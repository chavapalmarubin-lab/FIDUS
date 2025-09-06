import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { 
  Wallet,
  Plus,
  Copy,
  ExternalLink,
  CreditCard,
  Building,
  Bitcoin,
  Coins,
  QrCode,
  AlertCircle,
  CheckCircle2,
  Edit,
  Trash2
} from "lucide-react";
import apiAxios from "../utils/apiAxios";

// FIDUS Official Wallet Addresses (from the provided image)
const FIDUS_OFFICIAL_WALLETS = [
  {
    network: "ERC20",
    currency: "USDT",
    address: "0xDe2DC29591dBc6e540b63050D73E2E9430733A90",
    name: "FIDUS USDT (ERC20)",
    icon: <Coins className="h-5 w-5" />,
    color: "bg-green-600"
  },
  {
    network: "ERC20", 
    currency: "USDC",
    address: "0xDe2DC29591dBc6e540b63050D73E2E9430733A90",
    name: "FIDUS USDC (ERC20)",
    icon: <Coins className="h-5 w-5" />,
    color: "bg-blue-600"
  },
  {
    network: "TRC20",
    currency: "USDT", 
    address: "TGoTqWUhLMFQyAm3BeFUEwMuUPDMY4g3iG",
    name: "FIDUS USDT (TRC20)",
    icon: <Coins className="h-5 w-5" />,
    color: "bg-green-500"
  },
  {
    network: "TRC20",
    currency: "USDC",
    address: "TGoTqWUhLMFQyAm3BeFUEwMuUPDMY4g3iG", 
    name: "FIDUS USDC (TRC20)",
    icon: <Coins className="h-5 w-5" />,
    color: "bg-blue-500"
  },
  {
    network: "Bitcoin",
    currency: "BTC",
    address: "1JT2h9aQ6KnP2vjRiPT13Dvc3ASp9mQ6fj",
    name: "FIDUS Bitcoin",
    icon: <Bitcoin className="h-5 w-5" />,
    color: "bg-orange-500"
  },
  {
    network: "Ethereum",
    currency: "ETH", 
    address: "0xDe2DC29591dBc6e540b63050D73E2E9430733A90",
    name: "FIDUS Ethereum",
    icon: <Coins className="h-5 w-5" />,
    color: "bg-purple-600"
  }
];

const ClientWallet = ({ user }) => {
  const [clientWallets, setClientWallets] = useState([]);
  const [showAddWalletModal, setShowAddWalletModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [copiedAddress, setCopiedAddress] = useState(null);
  
  // Form state for adding new wallet
  const [newWallet, setNewWallet] = useState({
    wallet_type: "crypto",
    wallet_name: "",
    is_primary: false,
    crypto_info: {
      network: "",
      currency: "",
      address: "",
      memo_tag: ""
    },
    fiat_info: {
      bank_name: "",
      account_holder: "",
      account_number: "",
      routing_number: "",
      swift_code: "",
      country: "USA"
    },
    notes: ""
  });

  useEffect(() => {
    fetchClientWallets();
  }, []);

  const fetchClientWallets = async () => {
    try {
      setLoading(true);
      // This endpoint would need to be implemented
      const response = await apiAxios.get(`/client/${user.id}/wallets`);
      if (response.data.success) {
        setClientWallets(response.data.wallets || []);
      }
    } catch (err) {
      console.error("Error fetching wallets:", err);
      setError("Failed to load wallet information");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (address, walletName) => {
    try {
      await navigator.clipboard.writeText(address);
      setCopiedAddress(address);
      setTimeout(() => setCopiedAddress(null), 2000);
    } catch (err) {
      console.error("Failed to copy address:", err);
    }
  };

  const handleAddWallet = async () => {
    try {
      const response = await apiAxios.post(`/client/${user.id}/wallets`, newWallet);
      if (response.data.success) {
        await fetchClientWallets();
        setShowAddWalletModal(false);
        setNewWallet({
          wallet_type: "crypto",
          wallet_name: "",
          is_primary: false,
          crypto_info: { network: "", currency: "", address: "", memo_tag: "" },
          fiat_info: { bank_name: "", account_holder: "", account_number: "", routing_number: "", swift_code: "", country: "USA" },
          notes: ""
        });
      }
    } catch (err) {
      console.error("Error adding wallet:", err);
      setError("Failed to add wallet");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">Payment Wallets</h2>
          <p className="text-gray-400">Manage your payment methods and view FIDUS deposit addresses</p>
        </div>
        <Button 
          onClick={() => setShowAddWalletModal(true)}
          className="bg-cyan-600 hover:bg-cyan-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Wallet
        </Button>
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-4 flex items-center">
          <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
          <span className="text-red-400">{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* FIDUS Official Wallets - Where to Send Money */}
        <Card className="bg-slate-800 border-slate-600">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Building className="mr-2 h-5 w-5 text-cyan-400" />
              FIDUS Official Wallets
              <Badge className="ml-2 bg-cyan-900 text-cyan-300">Send Here</Badge>
            </CardTitle>
            <p className="text-gray-400 text-sm">Send your deposits to these FIDUS addresses</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {FIDUS_OFFICIAL_WALLETS.map((wallet, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border border-slate-600 rounded-lg p-4 hover:border-slate-500 transition-all"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <div className={`${wallet.color} rounded-lg p-2 text-white mr-3`}>
                        {wallet.icon}
                      </div>
                      <div>
                        <h4 className="font-semibold text-white">{wallet.name}</h4>
                        <p className="text-sm text-gray-400">{wallet.network} Network</p>
                      </div>
                    </div>
                    <Badge variant="outline" className="text-gray-300 border-gray-500">
                      {wallet.currency}
                    </Badge>
                  </div>
                  
                  <div className="bg-slate-900 rounded-lg p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300 font-mono text-sm break-all">
                        {wallet.address}
                      </span>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => copyToClipboard(wallet.address, wallet.name)}
                        className="ml-2 text-gray-400 hover:text-white"
                      >
                        {copiedAddress === wallet.address ? (
                          <CheckCircle2 className="h-4 w-4 text-green-400" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
            
            <div className="mt-4 p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg">
              <div className="flex items-start">
                <AlertCircle className="h-5 w-5 text-blue-400 mr-2 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-blue-300">
                  <p className="font-semibold mb-1">Important:</p>
                  <p>Only send the specified cryptocurrency to each address. Sending wrong tokens may result in permanent loss.</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Client Personal Wallets */}
        <Card className="bg-slate-800 border-slate-600">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Wallet className="mr-2 h-5 w-5 text-cyan-400" />
              Your Personal Wallets
              <Badge className="ml-2 bg-green-900 text-green-300">Receive Here</Badge>
            </CardTitle>
            <p className="text-gray-400 text-sm">Your wallets for receiving redemptions and payments</p>
          </CardHeader>
          <CardContent>
            {clientWallets.length === 0 ? (
              <div className="text-center py-8">
                <Wallet className="mx-auto h-12 w-12 text-gray-500 mb-4" />
                <p className="text-gray-400 mb-4">No wallets added yet</p>
                <Button 
                  onClick={() => setShowAddWalletModal(true)}
                  variant="outline"
                  className="border-cyan-600 text-cyan-400 hover:bg-cyan-600 hover:text-white"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Your First Wallet
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {clientWallets.map((wallet, index) => (
                  <motion.div
                    key={wallet.wallet_id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="border border-slate-600 rounded-lg p-4 hover:border-slate-500 transition-all"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center">
                        <div className="bg-gray-600 rounded-lg p-2 text-white mr-3">
                          {wallet.wallet_type === 'crypto' ? <Coins className="h-5 w-5" /> : <CreditCard className="h-5 w-5" />}
                        </div>
                        <div>
                          <h4 className="font-semibold text-white">{wallet.wallet_name}</h4>
                          <p className="text-sm text-gray-400">
                            {wallet.wallet_type === 'crypto' ? 
                              `${wallet.crypto_info?.currency} (${wallet.crypto_info?.network})` :
                              `${wallet.fiat_info?.bank_name}`
                            }
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {wallet.is_primary && (
                          <Badge className="bg-green-900 text-green-300">Primary</Badge>
                        )}
                        <Button size="sm" variant="ghost" className="text-gray-400 hover:text-white">
                          <Edit className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="bg-slate-900 rounded-lg p-3">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-300 font-mono text-sm break-all">
                          {wallet.wallet_type === 'crypto' ? 
                            wallet.crypto_info?.address :
                            `****${wallet.fiat_info?.account_number?.slice(-4)}`
                          }
                        </span>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copyToClipboard(
                            wallet.wallet_type === 'crypto' ? wallet.crypto_info?.address : wallet.fiat_info?.account_number,
                            wallet.wallet_name
                          )}
                          className="ml-2 text-gray-400 hover:text-white"
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Add Wallet Modal */}
      {showAddWalletModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-xl font-bold text-white mb-4">Add New Wallet</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Wallet Type</label>
                <select
                  value={newWallet.wallet_type}
                  onChange={(e) => setNewWallet({...newWallet, wallet_type: e.target.value})}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white"
                >
                  <option value="crypto">Cryptocurrency</option>
                  <option value="fiat">Bank Account</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Wallet Name</label>
                <input
                  type="text"
                  value={newWallet.wallet_name}
                  onChange={(e) => setNewWallet({...newWallet, wallet_name: e.target.value})}
                  placeholder="e.g., My Bitcoin Wallet"
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white"
                />
              </div>

              {newWallet.wallet_type === 'crypto' ? (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Network</label>
                      <select
                        value={newWallet.crypto_info.network}
                        onChange={(e) => setNewWallet({
                          ...newWallet,
                          crypto_info: {...newWallet.crypto_info, network: e.target.value}
                        })}
                        className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white"
                      >
                        <option value="">Select Network</option>
                        <option value="Bitcoin">Bitcoin</option>
                        <option value="Ethereum">Ethereum</option>
                        <option value="ERC20">ERC20</option>
                        <option value="TRC20">TRC20</option>
                        <option value="BSC">BSC</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Currency</label>
                      <input
                        type="text"
                        value={newWallet.crypto_info.currency}
                        onChange={(e) => setNewWallet({
                          ...newWallet,
                          crypto_info: {...newWallet.crypto_info, currency: e.target.value.toUpperCase()}
                        })}
                        placeholder="BTC, ETH, USDT"
                        className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Wallet Address</label>
                    <input
                      type="text"
                      value={newWallet.crypto_info.address}
                      onChange={(e) => setNewWallet({
                        ...newWallet,
                        crypto_info: {...newWallet.crypto_info, address: e.target.value}
                      })}
                      placeholder="Your wallet address"
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white"
                    />
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Bank Name</label>
                    <input
                      type="text"
                      value={newWallet.fiat_info.bank_name}
                      onChange={(e) => setNewWallet({
                        ...newWallet,
                        fiat_info: {...newWallet.fiat_info, bank_name: e.target.value}
                      })}
                      placeholder="Bank of America"
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Account Holder</label>
                    <input
                      type="text"
                      value={newWallet.fiat_info.account_holder}
                      onChange={(e) => setNewWallet({
                        ...newWallet,
                        fiat_info: {...newWallet.fiat_info, account_holder: e.target.value}
                      })}
                      placeholder="John Doe"
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Account Number</label>
                    <input
                      type="text"
                      value={newWallet.fiat_info.account_number}
                      onChange={(e) => setNewWallet({
                        ...newWallet,
                        fiat_info: {...newWallet.fiat_info, account_number: e.target.value}
                      })}
                      placeholder="1234567890"
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white"
                    />
                  </div>
                </>
              )}

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="primary"
                  checked={newWallet.is_primary}
                  onChange={(e) => setNewWallet({...newWallet, is_primary: e.target.checked})}
                  className="mr-2"
                />
                <label htmlFor="primary" className="text-sm text-gray-300">Set as primary wallet</label>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <Button
                variant="outline"
                onClick={() => setShowAddWalletModal(false)}
                className="border-gray-600 text-gray-300"
              >
                Cancel
              </Button>
              <Button
                onClick={handleAddWallet}
                className="bg-cyan-600 hover:bg-cyan-700"
                disabled={!newWallet.wallet_name || (newWallet.wallet_type === 'crypto' && !newWallet.crypto_info.address)}
              >
                Add Wallet
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClientWallet;