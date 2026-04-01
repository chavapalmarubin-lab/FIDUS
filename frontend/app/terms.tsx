import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useLanguage } from '../src/context/LanguageContext';
import { useAuth } from '../src/context/AuthContext';
import { translations } from '../src/i18n/translations';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Constants from 'expo-constants';

const API_BASE = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || 
                 process.env.EXPO_PUBLIC_BACKEND_URL || 
                 'https://retail-investor-hub.preview.emergentagent.com';

// LUCRUM Terms (Section 1)
const LUCRUM_TERMS = `LUCRUM CAPITAL LIMITED
CLIENT AGREEMENT & RISK DISCLOSURES

Lucrum Capital Limited is duly authorized and regulated by the Financial Services Commission of Mauritius (FSC) under License No. GB14203805.

Registered Address: The Catalyst, Level 2, Suite 201, Plot 40, Silicon Avenue, Ebene, Mauritius

EXECUTION-ONLY SERVICE
Lucrum Capital provides an execution-only brokerage service for CFDs, Forex, indices, commodities, and cryptocurrencies via the MetaTrader 5 (MT5) platform.

ACCOUNT TYPES
• Standard Accounts: Minimum USD 20, spreads from 1 pip
• ECN Accounts: Minimum USD 200, spreads from 0.2 pips

LEVERAGE & MARGIN
Lucrum Capital may apply leverage up to the maximum levels permitted under its FSC license and risk policies. Leverage magnifies both gains and losses.
• Margin Call: Triggered when equity falls below 100% of required margin
• Stop Out: Positions closed automatically when equity falls below 50% of required margin

SEGREGATED FUNDS
Client funds are held in segregated accounts in accordance with FSC requirements. However, Mauritius regulation may not provide the same level of investor protection as regulators in EU, UK, Australia, or the United States.

FEES AND COSTS
• Broker commissions
• Bid/ask spreads
• Overnight swap/rollover charges
• Account inactivity fees (accounts inactive for 90 days)
• Deposit and withdrawal processing fees
• Currency conversion costs

PROHIBITED PRACTICES
Lucrum Capital will close, suspend, or reclaim profits when abusive or prohibited practices are detected, including:
• Abuse of price gaps or latency arbitrage
• Order flooding or high-frequency trading exploiting platform micro-latencies
• Credential sharing or account use by unauthorized persons
• Use of unauthorized automated bots
• Market manipulation or fraud

DATA PROTECTION
Lucrum Capital processes client personal data in accordance with applicable data protection laws.

GOVERNING LAW
The Lucrum Capital Client Agreement is governed by the laws of the Republic of Mauritius.

AML/KYC REQUIREMENTS
Lucrum Capital requires clients to complete identity verification including:
• Proof of identity
• Proof of address
• Source of funds documentation

Lucrum Capital Limited
FSC Mauritius – License GB14203805
lucrumfx.com`;

// FIDUS Terms (Section 2)
const FIDUS_TERMS = `FIDUS SOLUTIONS LLC
MONEY MANAGER & INTRODUCING BROKER DISCLOSURES

FIDUS Solutions LLC is a multi-strategy money manager and Introducing Broker (IB) platform incorporated under the laws of Saint Kitts and Nevis.

REGULATORY STATUS
FIDUS is NOT registered with or regulated by:
• U.S. Securities and Exchange Commission (SEC)
• Commodity Futures Trading Commission (CFTC)
• FINRA or NFA
• Any comparable regulatory authority

SERVICES PROVIDED
FIDUS allocates client capital to independent Money Managers who execute trading strategies primarily in CFDs and Forex via Lucrum Capital's platform.

NO GUARANTEE OF RETURNS
FIDUS SOLUTIONS LLC MAKES NO GUARANTEE, REPRESENTATION, OR WARRANTY THAT ANY INVESTMENT STRATEGY, TRADING ACTIVITY, OR PORTFOLIO ALLOCATION WILL RESULT IN PROFITS OR PREVENT LOSSES. THERE IS NO GUARANTEE OF ANY MINIMUM RETURN. YOU MAY LOSE ALL OF YOUR INVESTED CAPITAL.

PAST PERFORMANCE DISCLAIMER
PAST PERFORMANCE IS NOT INDICATIVE OF FUTURE RESULTS. Historical returns, track records, backtested or simulated results do not guarantee future performance.

RISK DISCLOSURES
• Risk of Total Loss: You may lose all or more than your initial deposit
• Leverage Risk: Small market movements can have disproportionately large impacts
• Market Volatility: Financial markets are subject to extreme volatility
• Execution Risk: Orders may execute at different prices than requested
• Liquidity Risk: Markets may become illiquid due to unforeseen events

INVESTOR SUITABILITY
These services are NOT suitable for all investors. Participation is appropriate only for persons who:
• Can withstand a total loss of invested capital
• Understand leveraged CFD and Forex trading risks
• Are 18 years of age or older
• Do not require short-term liquidity from invested funds

NOT INVESTMENT ADVICE
Neither FIDUS Solutions LLC nor Lucrum Capital Limited provides personalized investment advice, financial advice, legal advice, or tax advice.

RESTRICTED JURISDICTIONS
Services are NOT available to residents of: United States, Canada, Iran, North Korea, Cuba, Myanmar, Syria, Venezuela, or sanctioned countries.

FIDUS Solutions LLC
Saint Kitts and Nevis
@getfidus`;

// Copy Trading Terms (Section 18)
const COPY_TRADING_TERMS = `COPY TRADING INVESTOR PARTICIPATION AGREEMENT
AND LIMITED TRADING AUTHORIZATION (LPOA)
Version 1.0 – Lucrum FX | Manager: FIDUS SOLUTIONS LLC

DEFINED PARTIES
• The Manager: FIDUS SOLUTIONS LLC — money manager and Introducing Broker incorporated in Saint Kitts and Nevis
• The Broker: LUCRUM CAPITAL LIMITED (Lucrum FX) — regulated executing broker (FSC Mauritius, License GB14203805)
• The Client: The retail investor authorizing copy trading

PURPOSE OF AGREEMENT
By accepting this Agreement, you expressly agree to:
• Participate in copy trading by appointing FIDUS SOLUTIONS LLC as authorized Manager
• Grant a Limited Power of Attorney (LPOA) for technical replication of trading signals
• Acknowledge Lucrum FX acts exclusively as broker and technology provider
• Accept all risks, fees, and conditions described herein

NATURE OF RELATIONSHIP
• Ownership of Funds: You retain full legal ownership of all funds at all times
• No Fiduciary Relationship: Copy trading does NOT create any fiduciary duty
• Voluntary Authorization: You are voluntarily electing to follow FIDUS SOLUTIONS LLC
• Limited Authorization: The LPOA does NOT authorize withdrawals or fund transfers

COPY TRADING RISK DISCLOSURE
BY AUTHORIZING FIDUS SOLUTIONS LLC AS YOUR MANAGER, YOU ACKNOWLEDGE:
• Past performance does NOT guarantee future results
• Performance differences may occur due to latency, slippage, spreads, or execution timing
• Lucrum FX makes no warranty regarding profitability or performance
• You have independently decided to authorize FIDUS SOLUTIONS LLC as Manager

ROLE OF FIDUS SOLUTIONS LLC (MANAGER)
FIDUS SOLUTIONS LLC:
• Is solely responsible for all trading signals and strategy decisions
• Does NOT act as agent, custodian, or representative of Lucrum FX
• Is NOT regulated by SEC, CFTC, FINRA, or NFA
• Acts as Introducing Broker and may receive compensation from Lucrum FX

FEES
You may be charged fees including:
• Management and/or performance fees
• Volume fees and subscription fees
• Broker commissions and spread markups
• Technology fees

ACTIVATION & TERMINATION
• You may activate or revoke copy trading through the Lucrum FX platform
• Revoking authorization does NOT automatically close open trades
• Lucrum FX or FIDUS may suspend the service at their discretion

LIMITATION OF LIABILITY
Lucrum FX and FIDUS SHALL NOT be liable for:
• Profitability or loss of any strategy
• Trading decisions or risk management of FIDUS
• Slippage, latency, or execution differences
• Technical failures beyond reasonable control

INVESTOR REPRESENTATIONS
You represent and warrant that:
• You understand the risks of copy trading
• You have read and accepted all agreements
• Your decision to authorize FIDUS is made independently and voluntarily
• You accept full responsibility for this decision

INDEMNIFICATION
You agree to indemnify and hold harmless Lucrum FX, FIDUS, and their affiliates from any loss or claim arising from your participation in copy trading.

This Agreement becomes effective upon your acceptance and constitutes a binding Limited Power of Attorney.`;

export default function TermsScreen() {
  const router = useRouter();
  const { language } = useLanguage();
  const { refreshUserData } = useAuth();
  const t = translations[language];

  const [lucrumExpanded, setLucrumExpanded] = useState(false);
  const [fidusExpanded, setFidusExpanded] = useState(false);
  const [copyTradingExpanded, setCopyTradingExpanded] = useState(false);
  
  const [lucrumAccepted, setLucrumAccepted] = useState(false);
  const [fidusAccepted, setFidusAccepted] = useState(false);
  const [copyTradingAccepted, setCopyTradingAccepted] = useState(false);
  
  const [isLoading, setIsLoading] = useState(false);

  const canProceed = lucrumAccepted && fidusAccepted && copyTradingAccepted;

  const handleAcceptTerms = async () => {
    if (!canProceed) {
      Alert.alert(t.error, t.mustAcceptAll);
      return;
    }

    setIsLoading(true);
    try {
      const token = await AsyncStorage.getItem('@fidus_auth_token');
      if (!token) {
        Alert.alert(t.error, 'Session expired. Please login again.');
        router.replace('/login');
        return;
      }

      const response = await axios.post(
        `${API_BASE}/api/user/accept-terms`,
        {
          lucrum_terms_accepted: true,
          fidus_terms_accepted: true,
          copy_trading_terms_accepted: true,
          user_agent: 'FIDUS Mobile App',
        },
        {
          headers: { Authorization: `Bearer ${token}` },
          timeout: 15000,
        }
      );

      if (response.data.success) {
        await refreshUserData();
        router.replace('/(tabs)');
      } else {
        Alert.alert(t.error, 'Failed to accept terms');
      }
    } catch (error: any) {
      console.error('Accept terms error:', error);
      Alert.alert(t.error, error?.response?.data?.detail || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>{t.termsAndConditions}</Text>
          <Text style={styles.headerSubtitle}>{t.pleaseReviewAndAccept}</Text>
        </View>

        {/* Warning Card */}
        <View style={styles.warningCard}>
          <Ionicons name="warning" size={24} color="#f59e0b" />
          <Text style={styles.warningText}>{t.highRiskWarning}</Text>
        </View>

        {/* 1. LUCRUM Terms Section */}
        <View style={styles.termsSection}>
          <TouchableOpacity
            style={styles.termsSectionHeader}
            onPress={() => setLucrumExpanded(!lucrumExpanded)}
          >
            <View style={styles.termsTitleContainer}>
              <View style={styles.termsBadge}>
                <Text style={styles.termsBadgeText}>1</Text>
              </View>
              <Ionicons name="business" size={24} color="#10b981" />
              <Text style={styles.termsSectionTitle}>Lucrum Capital Limited</Text>
            </View>
            <Ionicons
              name={lucrumExpanded ? 'chevron-up' : 'chevron-down'}
              size={24}
              color="#6b7280"
            />
          </TouchableOpacity>

          {lucrumExpanded && (
            <ScrollView style={styles.termsContent} nestedScrollEnabled>
              <Text style={styles.termsText}>{LUCRUM_TERMS}</Text>
            </ScrollView>
          )}

          <TouchableOpacity
            style={styles.checkboxContainer}
            onPress={() => setLucrumAccepted(!lucrumAccepted)}
          >
            <View style={[styles.checkbox, lucrumAccepted && styles.checkboxChecked]}>
              {lucrumAccepted && <Ionicons name="checkmark" size={16} color="#ffffff" />}
            </View>
            <Text style={styles.checkboxLabel}>{t.iAcceptLucrumTerms}</Text>
          </TouchableOpacity>
        </View>

        {/* 2. FIDUS Terms Section */}
        <View style={styles.termsSection}>
          <TouchableOpacity
            style={styles.termsSectionHeader}
            onPress={() => setFidusExpanded(!fidusExpanded)}
          >
            <View style={styles.termsTitleContainer}>
              <View style={styles.termsBadge}>
                <Text style={styles.termsBadgeText}>2</Text>
              </View>
              <Ionicons name="shield-checkmark" size={24} color="#00b4d8" />
              <Text style={styles.termsSectionTitle}>FIDUS Solutions LLC</Text>
            </View>
            <Ionicons
              name={fidusExpanded ? 'chevron-up' : 'chevron-down'}
              size={24}
              color="#6b7280"
            />
          </TouchableOpacity>

          {fidusExpanded && (
            <ScrollView style={styles.termsContent} nestedScrollEnabled>
              <Text style={styles.termsText}>{FIDUS_TERMS}</Text>
            </ScrollView>
          )}

          <TouchableOpacity
            style={styles.checkboxContainer}
            onPress={() => setFidusAccepted(!fidusAccepted)}
          >
            <View style={[styles.checkbox, fidusAccepted && styles.checkboxChecked]}>
              {fidusAccepted && <Ionicons name="checkmark" size={16} color="#ffffff" />}
            </View>
            <Text style={styles.checkboxLabel}>{t.iAcceptFidusTerms}</Text>
          </TouchableOpacity>
        </View>

        {/* 3. Copy Trading Terms Section */}
        <View style={styles.termsSection}>
          <TouchableOpacity
            style={styles.termsSectionHeader}
            onPress={() => setCopyTradingExpanded(!copyTradingExpanded)}
          >
            <View style={styles.termsTitleContainer}>
              <View style={styles.termsBadge}>
                <Text style={styles.termsBadgeText}>3</Text>
              </View>
              <Ionicons name="copy" size={24} color="#8b5cf6" />
              <Text style={styles.termsSectionTitle}>{t.copyTradingAgreement}</Text>
            </View>
            <Ionicons
              name={copyTradingExpanded ? 'chevron-up' : 'chevron-down'}
              size={24}
              color="#6b7280"
            />
          </TouchableOpacity>

          {copyTradingExpanded && (
            <ScrollView style={styles.termsContent} nestedScrollEnabled>
              <Text style={styles.termsText}>{COPY_TRADING_TERMS}</Text>
            </ScrollView>
          )}

          <TouchableOpacity
            style={styles.checkboxContainer}
            onPress={() => setCopyTradingAccepted(!copyTradingAccepted)}
          >
            <View style={[styles.checkbox, copyTradingAccepted && styles.checkboxChecked]}>
              {copyTradingAccepted && <Ionicons name="checkmark" size={16} color="#ffffff" />}
            </View>
            <Text style={styles.checkboxLabel}>{t.iAcceptCopyTradingTerms}</Text>
          </TouchableOpacity>
        </View>

        {/* Info Card */}
        <View style={styles.infoCard}>
          <Ionicons name="information-circle" size={20} color="#00b4d8" />
          <Text style={styles.infoText}>{t.termsLegalInfo}</Text>
        </View>

        {/* Accept Button */}
        <TouchableOpacity
          style={[
            styles.acceptButton,
            !canProceed && styles.acceptButtonDisabled,
            isLoading && styles.acceptButtonDisabled,
          ]}
          onPress={handleAcceptTerms}
          disabled={!canProceed || isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color="#0a0f1a" />
          ) : (
            <>
              <Ionicons name="checkmark-circle" size={20} color="#0a0f1a" />
              <Text style={styles.acceptButtonText}>{t.acceptAndContinue}</Text>
            </>
          )}
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0f1a',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingBottom: 32,
  },
  header: {
    paddingVertical: 24,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#ffffff',
    textAlign: 'center',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 8,
    textAlign: 'center',
  },
  warningCard: {
    backgroundColor: 'rgba(245, 158, 11, 0.15)',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#f59e0b',
  },
  warningText: {
    flex: 1,
    fontSize: 13,
    color: '#f59e0b',
    lineHeight: 20,
    fontWeight: '500',
  },
  termsSection: {
    backgroundColor: '#1a2332',
    borderRadius: 12,
    marginBottom: 16,
    overflow: 'hidden',
  },
  termsSectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
  },
  termsTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    flex: 1,
  },
  termsBadge: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#2a3444',
    justifyContent: 'center',
    alignItems: 'center',
  },
  termsBadgeText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#ffffff',
  },
  termsSectionTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#ffffff',
    flex: 1,
  },
  termsContent: {
    maxHeight: 250,
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  termsText: {
    fontSize: 12,
    color: '#9ca3af',
    lineHeight: 18,
  },
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#2a3444',
    gap: 12,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#6b7280',
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxChecked: {
    backgroundColor: '#00b4d8',
    borderColor: '#00b4d8',
  },
  checkboxLabel: {
    flex: 1,
    fontSize: 14,
    color: '#ffffff',
  },
  infoCard: {
    backgroundColor: 'rgba(0, 180, 216, 0.1)',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    marginBottom: 24,
  },
  infoText: {
    flex: 1,
    fontSize: 12,
    color: '#00b4d8',
    lineHeight: 18,
  },
  acceptButton: {
    backgroundColor: '#00b4d8',
    borderRadius: 12,
    height: 56,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
  },
  acceptButtonDisabled: {
    opacity: 0.5,
  },
  acceptButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#0a0f1a',
  },
});
