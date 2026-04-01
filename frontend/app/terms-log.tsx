import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useLanguage } from '../src/context/LanguageContext';
import { translations } from '../src/i18n/translations';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Constants from 'expo-constants';

const API_BASE = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || 
                 process.env.EXPO_PUBLIC_BACKEND_URL || 
                 'https://retail-investor-hub.preview.emergentagent.com';

interface TermsAcceptanceLog {
  id: string;
  user_id: string;
  user_email: string;
  user_name: string;
  lucrum_terms_accepted: boolean;
  fidus_terms_accepted: boolean;
  copy_trading_terms_accepted: boolean;
  terms_version: string;
  ip_address?: string;
  user_agent?: string;
  accepted_at: string;
}

export default function TermsLogScreen() {
  const router = useRouter();
  const { language } = useLanguage();
  const t = translations[language];

  const [acceptances, setAcceptances] = useState<TermsAcceptanceLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    fetchAcceptances();
    fetchCount();
  }, []);

  const fetchAcceptances = async () => {
    try {
      const token = await AsyncStorage.getItem('@fidus_auth_token');
      if (!token) return;

      const response = await axios.get(`${API_BASE}/api/admin/terms-acceptances?limit=100`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setAcceptances(response.data);
    } catch (error) {
      console.error('Error fetching acceptances:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCount = async () => {
    try {
      const token = await AsyncStorage.getItem('@fidus_auth_token');
      if (!token) return;

      const response = await axios.get(`${API_BASE}/api/admin/terms-acceptances/count`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setTotalCount(response.data.count);
    } catch (error) {
      console.error('Error fetching count:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([fetchAcceptances(), fetchCount()]);
    setRefreshing(false);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#ffffff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{t.viewTermsAcceptances}</Text>
      </View>

      {/* Stats Card */}
      <View style={styles.statsCard}>
        <Ionicons name="document-text" size={32} color="#00b4d8" />
        <View style={styles.statsInfo}>
          <Text style={styles.statsNumber}>{totalCount}</Text>
          <Text style={styles.statsLabel}>
            {language === 'es' ? 'Aceptaciones Totales' : 'Total Acceptances'}
          </Text>
        </View>
      </View>

      {/* Acceptances List */}
      {isLoading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#00b4d8" />
        </View>
      ) : (
        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor="#00b4d8"
            />
          }
        >
          {acceptances.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Ionicons name="document-outline" size={64} color="#6b7280" />
              <Text style={styles.emptyText}>
                {language === 'es' ? 'No hay aceptaciones aún' : 'No acceptances yet'}
              </Text>
            </View>
          ) : (
            acceptances.map((acceptance) => (
              <View key={acceptance.id} style={styles.acceptanceCard}>
                <View style={styles.acceptanceHeader}>
                  <View style={styles.userInfo}>
                    <View style={styles.avatar}>
                      <Text style={styles.avatarText}>
                        {acceptance.user_name?.charAt(0).toUpperCase() || 'U'}
                      </Text>
                    </View>
                    <View>
                      <Text style={styles.userName}>{acceptance.user_name}</Text>
                      <Text style={styles.userEmail}>{acceptance.user_email}</Text>
                    </View>
                  </View>
                  <Text style={styles.version}>v{acceptance.terms_version}</Text>
                </View>

                <View style={styles.acceptanceDetails}>
                  <View style={styles.detailRow}>
                    <Ionicons name="time-outline" size={16} color="#6b7280" />
                    <Text style={styles.detailText}>{formatDate(acceptance.accepted_at)}</Text>
                  </View>

                  <View style={styles.checkmarks}>
                    <View style={styles.checkItem}>
                      <Ionicons
                        name={acceptance.lucrum_terms_accepted ? 'checkmark-circle' : 'close-circle'}
                        size={18}
                        color={acceptance.lucrum_terms_accepted ? '#10b981' : '#ef4444'}
                      />
                      <Text style={styles.checkLabel}>LUCRUM</Text>
                    </View>
                    <View style={styles.checkItem}>
                      <Ionicons
                        name={acceptance.fidus_terms_accepted ? 'checkmark-circle' : 'close-circle'}
                        size={18}
                        color={acceptance.fidus_terms_accepted ? '#10b981' : '#ef4444'}
                      />
                      <Text style={styles.checkLabel}>FIDUS</Text>
                    </View>
                    <View style={styles.checkItem}>
                      <Ionicons
                        name={acceptance.copy_trading_terms_accepted ? 'checkmark-circle' : 'close-circle'}
                        size={18}
                        color={acceptance.copy_trading_terms_accepted ? '#10b981' : '#ef4444'}
                      />
                      <Text style={styles.checkLabel}>COPY</Text>
                    </View>
                  </View>

                  {acceptance.user_agent && (
                    <View style={styles.detailRow}>
                      <Ionicons name="phone-portrait-outline" size={16} color="#6b7280" />
                      <Text style={styles.detailText} numberOfLines={1}>
                        {acceptance.user_agent}
                      </Text>
                    </View>
                  )}
                </View>
              </View>
            ))
          )}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0f1a',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  backButton: {
    marginRight: 16,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#ffffff',
  },
  statsCard: {
    backgroundColor: '#1a2332',
    borderRadius: 12,
    padding: 20,
    marginHorizontal: 16,
    marginBottom: 16,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  statsInfo: {
    flex: 1,
  },
  statsNumber: {
    fontSize: 32,
    fontWeight: '700',
    color: '#00b4d8',
  },
  statsLabel: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 4,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingBottom: 24,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 16,
    color: '#6b7280',
    marginTop: 16,
  },
  acceptanceCard: {
    backgroundColor: '#1a2332',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  acceptanceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  userInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#00b4d8',
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  userName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  userEmail: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 2,
  },
  version: {
    fontSize: 12,
    color: '#00b4d8',
    backgroundColor: 'rgba(0, 180, 216, 0.1)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  acceptanceDetails: {
    borderTopWidth: 1,
    borderTopColor: '#2a3444',
    paddingTop: 12,
    gap: 8,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  detailText: {
    fontSize: 13,
    color: '#9ca3af',
    flex: 1,
  },
  checkmarks: {
    flexDirection: 'row',
    gap: 16,
  },
  checkItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  checkLabel: {
    fontSize: 12,
    color: '#9ca3af',
  },
});
