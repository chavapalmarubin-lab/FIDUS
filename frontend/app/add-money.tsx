import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Linking,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useLanguage } from '../src/context/LanguageContext';
import { translations } from '../src/i18n/translations';

export default function AddMoneyScreen() {
  const router = useRouter();
  const { language } = useLanguage();
  const t = translations[language];

  const handleOpenLucrum = () => {
    Linking.openURL('https://my.lucrumfx.com');
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#ffffff" />
          </TouchableOpacity>
          <View>
            <Text style={styles.headerTitle}>{t.addMoney}</Text>
            <Text style={styles.headerSubtitle}>{t.addMoneySubtitle}</Text>
          </View>
        </View>

        {/* Instructions Card */}
        <View style={styles.instructionsCard}>
          <Text style={styles.instructionsTitle}>{t.howToDeposit}</Text>
          
          <View style={styles.step}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>1</Text>
            </View>
            <View style={styles.stepContent}>
              <Text style={styles.stepText}>{t.depositStep1}</Text>
              <TouchableOpacity onPress={handleOpenLucrum}>
                <Text style={styles.linkText}>my.lucrumfx.com</Text>
              </TouchableOpacity>
            </View>
          </View>

          <View style={styles.step}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>2</Text>
            </View>
            <View style={styles.stepContent}>
              <Text style={styles.stepText}>{t.depositStep2}</Text>
            </View>
          </View>

          <View style={styles.step}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>3</Text>
            </View>
            <View style={styles.stepContent}>
              <Text style={styles.stepText}>{t.depositStep3}</Text>
            </View>
          </View>
        </View>

        {/* Payment Methods */}
        <View style={styles.methodsContainer}>
          <Text style={styles.methodsTitle}>{t.paymentMethods}</Text>
          <View style={styles.methodsGrid}>
            <View style={styles.methodItem}>
              <Ionicons name="card-outline" size={24} color="#00b4d8" />
              <Text style={styles.methodText}>{t.bankTransfer}</Text>
            </View>
            <View style={styles.methodItem}>
              <Ionicons name="logo-bitcoin" size={24} color="#f7931a" />
              <Text style={styles.methodText}>Crypto</Text>
            </View>
            <View style={styles.methodItem}>
              <Ionicons name="card" size={24} color="#10b981" />
              <Text style={styles.methodText}>{t.creditCard}</Text>
            </View>
          </View>
        </View>

        {/* Go to Lucrum Button */}
        <TouchableOpacity style={styles.lucrumButton} onPress={handleOpenLucrum}>
          <Text style={styles.lucrumButtonText}>{t.goToLucrum}</Text>
          <Ionicons name="open-outline" size={20} color="#0a0f1a" />
        </TouchableOpacity>

        {/* Info Note */}
        <View style={styles.infoCard}>
          <Ionicons name="shield-checkmark" size={24} color="#10b981" />
          <Text style={styles.infoText}>{t.depositInfo}</Text>
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
  headerSubtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 4,
  },
  instructionsCard: {
    backgroundColor: '#1a2332',
    borderRadius: 12,
    padding: 20,
    marginTop: 16,
    borderWidth: 1,
    borderColor: '#10b981',
  },
  instructionsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#10b981',
    marginBottom: 20,
  },
  step: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  stepNumber: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: 'rgba(16, 185, 129, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  stepNumberText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#10b981',
  },
  stepContent: {
    flex: 1,
  },
  stepText: {
    fontSize: 14,
    color: '#ffffff',
    lineHeight: 22,
  },
  linkText: {
    fontSize: 14,
    color: '#00b4d8',
    marginTop: 4,
  },
  methodsContainer: {
    marginTop: 24,
  },
  methodsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
    marginBottom: 12,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  methodsGrid: {
    flexDirection: 'row',
    gap: 12,
  },
  methodItem: {
    flex: 1,
    backgroundColor: '#1a2332',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    gap: 8,
  },
  methodText: {
    fontSize: 12,
    color: '#ffffff',
    textAlign: 'center',
  },
  lucrumButton: {
    backgroundColor: '#10b981',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    marginTop: 24,
  },
  lucrumButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#0a0f1a',
  },
  infoCard: {
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    marginTop: 16,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#10b981',
    lineHeight: 20,
  },
});
