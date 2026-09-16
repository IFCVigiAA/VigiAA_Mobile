import { MaterialCommunityIcons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

const API_URL = "https://froglike-cataleya-quirkily.ngrok-free.dev";

export default function PositiveCaseFormScreen({ navigation }) {
  const [nomePaciente, setNomePaciente] = useState('');
  const [dataConfirmacao, setDataConfirmacao] = useState('');
  const [observacoes, setObservacoes] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!nomePaciente) {
      Alert.alert("Aviso", "Preencha o nome do paciente.");
      return;
    }

    setLoading(true);
    try {
      const token = await AsyncStorage.getItem('session_token');
      
      const response = await fetch(`${API_URL}/api/casos-positivos/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({
          nome_paciente: nomePaciente,
          data_confirmacao: dataConfirmacao,
          observacoes: observacoes
        })
      });

      if (response.ok) {
        Alert.alert("Sucesso", "Caso positivo registrado com sucesso!");
        navigation.goBack();
      } else {
        Alert.alert("Erro", "Não foi possível registrar o caso positivo.");
      }
    } catch (error) {
      Alert.alert("Erro", "Erro de conexão com o servidor.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <MaterialCommunityIcons name="arrow-left" size={24} color="#000" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Cadastrar Caso Positivo</Text>
      </View>

      <ScrollView contentContainerStyle={styles.formContainer}>
        <Text style={styles.label}>Nome do Paciente</Text>
        <TextInput
          style={styles.input}
          placeholder="Nome completo"
          value={nomePaciente}
          onChangeText={setNomePaciente}
        />

        <Text style={styles.label}>Data da Confirmação</Text>
        <TextInput
          style={styles.input}
          placeholder="AAAA-MM-DD"
          value={dataConfirmacao}
          onChangeText={setDataConfirmacao}
        />

        <Text style={styles.label}>Observações Médicas</Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          placeholder="Detalhes do diagnóstico..."
          value={observacoes}
          onChangeText={setObservacoes}
          multiline
          numberOfLines={4}
        />

        <TouchableOpacity style={styles.submitButton} onPress={handleSubmit} disabled={loading}>
          <Text style={styles.submitButtonText}>{loading ? "Enviando..." : "Salvar Caso Positivo"}</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F5F5' },
  header: { height: 90, paddingTop: 35, paddingHorizontal: 20, flexDirection: 'row', alignItems: 'center', backgroundColor: '#FFF', borderBottomWidth: 1, borderBottomColor: '#E0E0E0' },
  backButton: { marginRight: 15 },
  headerTitle: { fontSize: 20, fontWeight: 'bold', color: '#000' },
  formContainer: { padding: 20 },
  label: { fontSize: 14, fontWeight: 'bold', color: '#333', marginBottom: 5, marginTop: 10 },
  input: { borderWidth: 1, borderColor: '#CCC', borderRadius: 8, height: 50, paddingHorizontal: 15, backgroundColor: '#FFF', color: '#000', marginBottom: 10 },
  textArea: { height: 100, textAlignVertical: 'top', paddingTop: 12 },
  submitButton: { backgroundColor: '#3AC0ED', height: 50, borderRadius: 8, alignItems: 'center', justifyContent: 'center', marginTop: 20 },
  submitButtonText: { color: '#000', fontWeight: 'bold', fontSize: 16 },
});