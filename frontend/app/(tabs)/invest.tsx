import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useLanguage } from '../../src/context/LanguageContext';
import { useAuth } from '../../src/context/AuthContext';
import { translations } from '../../src/i18n/translations';

const INVESTMENT_OPTIONS = [500, 1000, 5000, 10000, 25000];

export default function InvestScreen() {
  const router = useRouter();
  const { language } = useLanguage();
  const { user } = useAuth();
  const t = translations[language];

  const [selectedAmount, setSelectedAmount] = useState(1000);

  const currentMonthly = (user?.balance || 0) * 0.015;
  const newMonthly = ((user?.balance || 0) + selectedAmount) * 0.015;
  const currentAnnual = currentMonthly * 12;
  const newAnnual = newMonthly * 12;

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#ffffff" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>{t.investmentSimulator}</Text>
        </View>

        <Text style={styles.subtitle}>{t.simulatorSubtitle}</Text>

        {/* Amount Options */}
        <View style={styles.optionsContainer}>
          {INVESTMENT_OPTIONS.map((amount) => (
            <TouchableOpacity
              key={amount}
              style={[
                styles.optionButton,
                selectedAmount === amount && styles.optionButtonSelected,
              ]}
              onPress={() => setSelectedAmount(amount)}
            >
              <Text
                style={[
                  styles.optionText,
                  selectedAmount === amount && styles.optionTextSelected,
                ]}
              >
                +{formatCurrency(amount)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Selected Amount Display */}
        <View style={styles.selectedDisplay}>
          <Text style={styles.selectedAmount}>
            +{formatCurrency(selectedAmount)}
          </Text>
          <Text style={styles.selectedLabel}>{t.additionalDeposit}</Text>
        </View>

        {/* Results */}
        <View style={styles.resultsContainer}>
          <View style={styles.resultRow}>
            <View style={styles.resultCard}>
              <Text style={styles.resultLabel}>{t.currentMonthly}</Text>
              <Text style={styles.resultAmount}>{formatCurrency(currentMonthly)}</Text>
            </View>
            <View style={[styles.resultCard, styles.resultCardHighlight]}>
              <Text style={styles.resultLabel}>{t.newMonthly}</Text>
              <Text style={[styles.resultAmount, styles.resultAmountHighlight]}>
                {formatCurrency(newMonthly)}
              </Text>
            </View>
          </View>

          <View style={styles.resultRow}>
            <View style={styles.resultCard}>
              <Text style={styles.resultLabel}>{t.currentAnnual}</Text>
              <Text style={styles.resultAmount}>{formatCurrency(currentAnnual)}</Text>
            </View>
            <View style={[styles.resultCard, styles.resultCardHighlight]}>
              <Text style={styles.resultLabel}>{t.newAnnual}</Text>
              <Text style={[styles.resultAmount, styles.resultAmountHighlight]}>
                {formatCurrency(newAnnual)}
              </Text>
            </View>
          </View>
        </View>

        {/* Info Card */}
        <View style={styles.infoCard}>
          <Ionicons name="information-circle" size={24} color="#00b4d8" />
          <Text style={styles.infoText}>{t.simulatorInfo}</Text>
        </View>
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
    paddingBottom: 24,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
  },
  backButton: {
    marginRight: 16,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#ffffff',
  },
  subtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 24,
  },
  optionsContainer: {
    gap: 12,
    marginBottom: 24,
  },
  optionButton: {
    backgroundColor: '#1a2332',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#2a3444',
  },
  optionButtonSelected: {
    backgroundColor: '#00b4d8',
    borderColor: '#00b4d8',
  },
  optionText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  optionTextSelected: {
    color: '#0a0f1a',
  },
  selectedDisplay: {
    alignItems: 'center',
    marginBottom: 32,
  },
  selectedAmount: {
    fontSize: 36,
    fontWeight: '700',
    color: '#00b4d8',
  },
  selectedLabel: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 8,
  },
  resultsContainer: {
    gap: 12,
    marginBottom: 24,
  },
  resultRow: {
    flexDirection: 'row',
    gap: 12,
  },
  resultCard: {
    flex: 1,
    backgroundColor: '#1a2332',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  resultCardHighlight: {
    borderWidth: 1,
    borderColor: '#00b4d8',
  },
  resultLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 8,
  },
  resultAmount: {
    fontSize: 20,
    fontWeight: '600',
    color: '#ffffff',
  },
  resultAmountHighlight: {
    color: '#00b4d8',
  },
  infoCard: {
    backgroundColor: 'rgba(0, 180, 216, 0.1)',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#00b4d8',
    lineHeight: 20,
  },
});
