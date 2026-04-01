import React from 'react';
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
import { translations } from '../../src/i18n/translations';

export default function InfoScreen() {
  const router = useRouter();
  const { language } = useLanguage();
  const t = translations[language];

  const faqs = [
    {
      question: t.faq1Question,
      answer: t.faq1Answer,
    },
    {
      question: t.faq2Question,
      answer: t.faq2Answer,
    },
    {
      question: t.faq3Question,
      answer: t.faq3Answer,
    },
    {
      question: t.faq4Question,
      answer: t.faq4Answer,
    },
    {
      question: t.faq5Question,
      answer: t.faq5Answer,
    },
    {
      question: t.faq6Question,
      answer: t.faq6Answer,
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#ffffff" />
          </TouchableOpacity>
          <View>
            <Text style={styles.headerTitle}>FIDUS CORE</Text>
            <Text style={styles.headerSubtitle}>{t.retailProduct}</Text>
          </View>
        </View>

        {/* FAQ Items */}
        <View style={styles.faqContainer}>
          {faqs.map((faq, index) => (
            <View key={index} style={styles.faqItem}>
              <Text style={styles.faqQuestion}>{faq.question}</Text>
              <Text style={styles.faqAnswer}>{faq.answer}</Text>
            </View>
          ))}
        </View>

        {/* Contact Card */}
        <View style={styles.contactCard}>
          <Ionicons name="help-circle" size={24} color="#00b4d8" />
          <View style={styles.contactContent}>
            <Text style={styles.contactTitle}>{t.needHelp}</Text>
            <Text style={styles.contactText}>{t.contactSupport}</Text>
          </View>
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
    color: '#00b4d8',
    marginTop: 4,
  },
  faqContainer: {
    gap: 12,
    marginTop: 16,
  },
  faqItem: {
    backgroundColor: '#1a2332',
    borderRadius: 12,
    padding: 16,
  },
  faqQuestion: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 8,
  },
  faqAnswer: {
    fontSize: 14,
    color: '#9ca3af',
    lineHeight: 22,
  },
  contactCard: {
    backgroundColor: 'rgba(0, 180, 216, 0.1)',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    marginTop: 24,
  },
  contactContent: {
    flex: 1,
  },
  contactTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 4,
  },
  contactText: {
    fontSize: 14,
    color: '#00b4d8',
  },
});
