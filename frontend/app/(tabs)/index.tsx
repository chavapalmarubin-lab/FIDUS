import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useLanguage } from '../../src/context/LanguageContext';
import { useAuth } from '../../src/context/AuthContext';
import { translations } from '../../src/i18n/translations';

export default function HomeScreen() {
  const router = useRouter();
  const { language } = useLanguage();
  const { user, refreshUserData, isLoading } = useAuth();
  const t = translations[language];

  const [refreshing, setRefreshing] = React.useState(false);

  const onRefresh = React.useCallback(async () => {
    setRefreshing(true);
    await refreshUserData();
    setRefreshing(false);
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const quickActions = [
    { icon: 'add', label: t.addMoney, color: '#1a2332', route: '/add-money' },
    { icon: 'remove', label: t.withdraw, color: '#1a2332', route: '/withdraw' },
    { icon: 'cube-outline', label: t.product, color: '#1a2332', route: '/(tabs)/info' },
    { icon: 'calculator-outline', label: t.simulator, color: '#1a2332', route: '/(tabs)/invest' },
  ];

  return (
    <SafeAreaView style={styles.container}>
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
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            <View style={styles.logoSmall}>
              <Ionicons name="trending-up" size={16} color="#00b4d8" />
            </View>
            <View>
              <Text style={styles.welcomeText}>{t.welcome}</Text>
              <Text style={styles.userName}>{user?.name || 'User'}</Text>
            </View>
          </View>
        </View>

        {/* Balance Card */}
        <View style={styles.balanceCard}>
          <Text style={styles.balanceLabel}>{t.totalBalance}</Text>
          <Text style={styles.balanceAmount}>
            {formatCurrency(user?.balance || 0)}
          </Text>
          <Text style={styles.earningsText}>
            +{formatCurrency(user?.totalEarnings || 0)} {t.earned}
          </Text>
          <View style={styles.badges}>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>1.5% {t.monthly}</Text>
            </View>
            <View style={[styles.badge, styles.badgePrimary]}>
              <Text style={[styles.badgeText, styles.badgeTextPrimary]}>FIDUS CORE</Text>
            </View>
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.actionsContainer}>
          {quickActions.map((action, index) => (
            <TouchableOpacity
              key={index}
              style={styles.actionButton}
              onPress={() => router.push(action.route as any)}
            >
              <View style={[styles.actionIcon, { backgroundColor: action.color }]}>
                <Ionicons name={action.icon as any} size={24} color="#ffffff" />
              </View>
              <Text style={styles.actionLabel}>{action.label}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Next Payment */}
        <View style={styles.nextPaymentCard}>
          <View>
            <Text style={styles.nextPaymentLabel}>{t.nextPayment}</Text>
            <Text style={styles.nextPaymentAmount}>
              {formatCurrency(user?.monthlyReturn || 0)}
            </Text>
          </View>
          <View style={styles.nextPaymentRight}>
            <Text style={styles.endOfMonth}>{t.endOfMonth}</Text>
            <Text style={styles.returnRate}>1.5% {t.returnLabel}</Text>
          </View>
        </View>

        {/* Payment Schedule */}
        <View style={styles.scheduleContainer}>
          <Text style={styles.scheduleTitle}>{t.paymentSchedule}</Text>
          {(user?.paymentSchedule || []).map((payment, index) => (
            <View key={index} style={styles.scheduleItem}>
              <View style={styles.scheduleLeft}>
                <View style={[styles.statusDot, payment.status === 'Funded' && styles.statusDotFunded]} />
                <Text style={styles.scheduleMonth}>{payment.month}</Text>
              </View>
              <View style={styles.scheduleRight}>
                <Text style={styles.scheduleAmount}>{formatCurrency(payment.amount)}</Text>
                <Text style={[styles.scheduleStatus, payment.status === 'Funded' && styles.scheduleStatusFunded]}>
                  {payment.status === 'Funded' ? t.funded : t.pending}
                </Text>
              </View>
            </View>
          ))}
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
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 16,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logoSmall: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: 'rgba(0, 180, 216, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  welcomeText: {
    fontSize: 12,
    color: '#6b7280',
  },
  userName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
  },
  balanceCard: {
    backgroundColor: '#1a2332',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    marginBottom: 20,
  },
  balanceLabel: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 8,
  },
  balanceAmount: {
    fontSize: 36,
    fontWeight: '700',
    color: '#ffffff',
    letterSpacing: 1,
  },
  earningsText: {
    fontSize: 14,
    color: '#10b981',
    marginTop: 8,
  },
  badges: {
    flexDirection: 'row',
    marginTop: 16,
    gap: 8,
  },
  badge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#00b4d8',
  },
  badgePrimary: {
    backgroundColor: '#00b4d8',
    borderColor: '#00b4d8',
  },
  badgeText: {
    fontSize: 12,
    color: '#00b4d8',
    fontWeight: '500',
  },
  badgeTextPrimary: {
    color: '#0a0f1a',
  },
  actionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  actionButton: {
    alignItems: 'center',
    flex: 1,
  },
  actionIcon: {
    width: 56,
    height: 56,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#2a3444',
  },
  actionLabel: {
    fontSize: 12,
    color: '#ffffff',
    textAlign: 'center',
  },
  nextPaymentCard: {
    backgroundColor: '#1a2332',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  nextPaymentLabel: {
    fontSize: 12,
    color: '#6b7280',
  },
  nextPaymentAmount: {
    fontSize: 24,
    fontWeight: '600',
    color: '#ffffff',
    marginTop: 4,
  },
  nextPaymentRight: {
    alignItems: 'flex-end',
  },
  endOfMonth: {
    fontSize: 14,
    color: '#10b981',
    fontWeight: '500',
  },
  returnRate: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 4,
  },
  scheduleContainer: {
    backgroundColor: '#1a2332',
    borderRadius: 12,
    padding: 16,
  },
  scheduleTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 16,
  },
  scheduleItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#2a3444',
  },
  scheduleLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#6b7280',
    marginRight: 12,
  },
  statusDotFunded: {
    backgroundColor: '#10b981',
  },
  scheduleMonth: {
    fontSize: 16,
    color: '#ffffff',
  },
  scheduleRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  scheduleAmount: {
    fontSize: 16,
    color: '#10b981',
  },
  scheduleStatus: {
    fontSize: 12,
    color: '#6b7280',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    backgroundColor: '#2a3444',
  },
  scheduleStatusFunded: {
    color: '#10b981',
  },
});
