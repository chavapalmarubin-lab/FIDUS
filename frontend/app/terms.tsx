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

// FIDUS and LUCRUM Combined Terms and Conditions
const FIDUS_TERMS = `FIDUS SOLUTIONS LLC in partnership with LUCRUM CAPITAL LIMITED
Quant Discipline. Human Insight. Fiduciary Purpose.

COMBINED RETAIL INVESTOR RISK DISCLOSURES & DISCLAIMERS
Effective Date: April 2026 | Version 1.0

HIGH RISK INVESTMENT WARNING: Trading Foreign Exchange (Forex) and Contracts for Differences (CFDs) is highly speculative, carries a HIGH LEVEL OF RISK, and is NOT SUITABLE FOR ALL INVESTORS. You may lose SOME OR ALL of your invested capital. Do NOT trade with money you cannot afford to lose. Past performance is NOT indicative of future results. Neither FIDUS SOLUTIONS LLC nor LUCRUM CAPITAL LIMITED guarantees any return, profit, or protection of capital.

1. The Parties — Who You Are Dealing With

This document is issued jointly by FIDUS SOLUTIONS LLC ("FIDUS") and Lucrum Capital Limited ("Lucrum FX" or "Lucrum Capital"), and governs the retail investor relationship across both entities.

FIDUS SOLUTIONS LLC
• Role: Money Manager & Introducing Broker
• Jurisdiction: Saint Kitts and Nevis
• Regulation: Not regulated by SEC/CFTC/FINRA
• Min. Retail Investment: USD 3,000

LUCRUM CAPITAL LIMITED
• Role: Executing Broker / Platform
• Jurisdiction: Mauritius
• License: FSC Mauritius – GB14203805
• Platform: MetaTrader 5 (MT5)

1.1 FIDUS Solutions LLC

FIDUS Solutions LLC ("FIDUS") is a multi-strategy money manager and Introducing Broker (IB) platform incorporated under the laws of Saint Kitts and Nevis. FIDUS allocates client capital to independent Money Managers who execute trading strategies primarily in CFDs and Forex via Lucrum Capital's platform. FIDUS is NOT registered with or regulated by the U.S. Securities and Exchange Commission (SEC), the Commodity Futures Trading Commission (CFTC), FINRA, the NFA, or any comparable regulatory authority.

1.2 Lucrum Capital Limited (Lucrum FX)

Lucrum Capital Limited is the executing broker and trading platform provider. It is duly authorized and regulated by the Financial Services Commission of Mauritius (FSC) under License No. GB14203805.

2. No Guarantee of Returns or Profits

NEITHER FIDUS SOLUTIONS LLC NOR LUCRUM CAPITAL LIMITED MAKES ANY GUARANTEE, REPRESENTATION, OR WARRANTY THAT ANY INVESTMENT STRATEGY, TRADING ACTIVITY, OR PORTFOLIO ALLOCATION WILL RESULT IN PROFITS OR PREVENT LOSSES. THERE IS NO GUARANTEE OF ANY MINIMUM RETURN. YOU MAY LOSE ALL OF YOUR INVESTED CAPITAL.

3. Past Performance Disclaimer

PAST PERFORMANCE IS NOT INDICATIVE OF FUTURE RESULTS. Historical returns, track records, backtested or simulated results do not guarantee future performance and may not reflect actual trading outcomes.

4. Comprehensive Risk Disclosures

4.1 Risk of Total Loss of Capital
The value of your investment may fall as well as rise. In leveraged instruments such as CFDs and Forex, you may lose all or more than your initial deposit.

4.2 Leverage & Margin Risk
CFDs and Forex are leveraged products. A small market movement can have a disproportionately large impact on invested capital.

4.3 Market, Volatility & Gap Risk
Financial markets are subject to extreme volatility, rapid price movements, and gap risk.

4.4 Execution, Slippage & Requote Risk
In conditions of high volatility or low liquidity, orders may execute at a price different from the requested price.

4.5 Liquidity Risk
Certain markets may become illiquid due to unforeseen economic or political events.

4.6 Overnight Financing (Swap/Rollover) Risk
Positions held open overnight are subject to swap or rollover charges or credits.

4.7 Currency & Exchange Rate Risk
Investments denominated in foreign currencies are subject to exchange rate fluctuations.

4.8 Counterparty & Broker Risk
Client funds are held by Lucrum Capital Limited, a regulated entity under FSC Mauritius.

5. Investor Suitability

THESE SERVICES ARE NOT SUITABLE FOR ALL INVESTORS. DO NOT INVEST MONEY THAT YOU CANNOT AFFORD TO LOSE.

Participation is appropriate only for persons who:
• Can withstand a total loss of invested capital without affecting their standard of living
• Understand the nature and risks of leveraged CFD and Forex trading
• Have sufficient knowledge and experience to evaluate the merits and risks independently
• Do not require short-term liquidity from the invested funds
• Are 18 years of age or older

6. Not Investment Advice

Neither FIDUS Solutions LLC nor Lucrum Capital Limited provides personalized investment advice, financial advice, legal advice, or tax advice.

7. Regulatory Status & Jurisdictional Restrictions

7.1 FIDUS Solutions LLC — Regulatory Status
FIDUS Solutions LLC is incorporated in Saint Kitts and Nevis and is NOT regulated by the U.S. SEC, CFTC, FINRA, NFA, or any comparable regulatory authority.

7.2 Lucrum Capital Limited — Regulatory Status
Lucrum Capital Limited is duly authorized and regulated by the Financial Services Commission of Mauritius (FSC) under License No. GB14203805.

7.3 Restricted Jurisdictions
These services are NOT available to residents of: United States of America, Canada, Iran, North Korea, Cuba, Myanmar, Syria, Venezuela, or any country subject to international sanctions.

15. Limitation of Liability

TO THE FULLEST EXTENT PERMITTED BY APPLICABLE LAW, NEITHER FIDUS SOLUTIONS LLC NOR LUCRUM CAPITAL LIMITED SHALL BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING FROM ANY INVESTMENT OR TRADING ACTIVITY.

18. Investor Acknowledgment & Declarations

By investing through FIDUS Solutions LLC and/or opening a trading account with Lucrum Capital Limited, I acknowledge and declare that:

• I have read, understood, and accept all risk warnings and disclosures in this document
• I understand that trading CFDs and Forex is highly speculative and involves the risk of losing my entire investment
• I have independently assessed my financial situation and determined that this investment is suitable for me
• I am not relying on any guarantee, promise, or projection of future performance
• I understand that FIDUS Solutions LLC is NOT regulated by the SEC, CFTC, FINRA, or NFA
• I understand that Lucrum Capital Limited is regulated by the FSC of Mauritius (License GB14203805)
• I confirm that I am NOT a resident of any restricted jurisdiction
• I acknowledge that my funds are NOT FDIC-insured, SIPC-protected, or covered by any governmental guarantee scheme
• I confirm that I am 18 years of age or older
• I declare that all funds I am investing are from legitimate sources

FIDUS Solutions LLC (Saint Kitts & Nevis) • Lucrum Capital Limited (Mauritius – FSC License GB14203805)
@getfidus • lucrumfx.com • Effective April 2026`;

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

Lucrum Capital processes client personal data in accordance with applicable data protection laws. By opening an account, the client consents to the collection, storage, processing, and transfer of personal data.

GOVERNING LAW

The Lucrum Capital Client Agreement is governed by the laws of the Republic of Mauritius.

AML/KYC REQUIREMENTS

Lucrum Capital requires clients to complete identity verification including:
• Proof of identity
• Proof of address
• Source of funds documentation

Client payments must ONLY be made to official payment methods designated by Lucrum Capital.

By accepting these terms, you confirm that you have read and understood the Lucrum Capital Client Agreement, Risk Notice, Order Execution Policy, Conflicts of Interest Policy, and Privacy Policy.

Lucrum Capital Limited
FSC Mauritius – License GB14203805
lucrumfx.com • info@lucrumfx.com`;

export default function TermsScreen() {
  const router = useRouter();
  const { language } = useLanguage();
  const { refreshUserData } = useAuth();
  const t = translations[language];

  const [fidusExpanded, setFidusExpanded] = useState(false);
  const [lucrumExpanded, setLucrumExpanded] = useState(false);
  const [fidusAccepted, setFidusAccepted] = useState(false);
  const [lucrumAccepted, setLucrumAccepted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const canProceed = fidusAccepted && lucrumAccepted;

  const handleAcceptTerms = async () => {
    if (!canProceed) {
      Alert.alert(t.error, t.mustAcceptBoth);
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
          fidus_terms_accepted: true,
          lucrum_terms_accepted: true,
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

        {/* FIDUS Terms Section */}
        <View style={styles.termsSection}>
          <TouchableOpacity
            style={styles.termsSectionHeader}
            onPress={() => setFidusExpanded(!fidusExpanded)}
          >
            <View style={styles.termsTitleContainer}>
              <Ionicons name="document-text" size={24} color="#00b4d8" />
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

        {/* LUCRUM Terms Section */}
        <View style={styles.termsSection}>
          <TouchableOpacity
            style={styles.termsSectionHeader}
            onPress={() => setLucrumExpanded(!lucrumExpanded)}
          >
            <View style={styles.termsTitleContainer}>
              <Ionicons name="document-text" size={24} color="#10b981" />
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
    gap: 12,
  },
  termsSectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  termsContent: {
    maxHeight: 300,
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
